import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        try:
            # Initialize embeddings
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                logger.warning("GOOGLE_API_KEY not found. Embeddings may not work.")
                self.embeddings = None
            else:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=google_api_key
                )
            
            # Initialize Pinecone
            self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
            self.index_name = os.getenv("PINECONE_INDEX_NAME", "chat-pdf-index")
            
            if not self.pinecone_api_key:
                logger.warning("PINECONE_API_KEY not found. Vector storage may not work.")
                self.pc = None
            else:
                # Initialize Pinecone with new API
                self.pc = Pinecone(api_key=self.pinecone_api_key)
                
                # Check if index exists, create if not
                try:
                    self.pc.describe_index(self.index_name)
                    logger.info(f"Using existing Pinecone index: {self.index_name}")
                except:
                    logger.info(f"Creating new Pinecone index: {self.index_name}")
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=768,  # Google embeddings dimension
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                    
        except Exception as e:
            logger.error(f"Error initializing Vector Service: {str(e)}")
            self.embeddings = None
            self.pc = None
        
    def store_document_vectors(self, text_chunks: List[str], namespace: str):
        """Store document text chunks as vectors in Pinecone with namespace"""
        try:
            if not self.embeddings or not self.pc:
                logger.error("Vector service not properly configured. Cannot store vectors.")
                raise ValueError("Vector service not configured")

            logger.info(f"Starting to store {len(text_chunks)} chunks in namespace {namespace}")
            logger.info(f"Pinecone client type: {type(self.pc)}")
            logger.info(f"Index name: {self.index_name}")
            
            # Get the index object
            index = self.pc.Index(self.index_name)
            logger.info(f"Index object created successfully: {type(index)}")
            
            # Generate embeddings for all chunks
            embeddings_list = self.embeddings.embed_documents(text_chunks)
            logger.info(f"Generated {len(embeddings_list)} embeddings")
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings_list)):
                vector_id = f"{namespace}_chunk_{i}"
                metadata = {
                    'namespace': namespace,
                    'chunk_index': i,
                    'source': f"document_chunk_{i}",
                    'type': 'document',
                    'text': chunk[:1000]  # Store first 1000 chars of text
                }
                vectors_to_upsert.append((vector_id, embedding, metadata))
            
            # Upsert vectors to Pinecone
            index.upsert(vectors=vectors_to_upsert, namespace=namespace)
            logger.info(f"✅ Stored {len(text_chunks)} chunks in namespace {namespace}")
            
            # Wait a moment for Pinecone to process the vectors
            import time
            time.sleep(2)
            
            # Verify the vectors were stored by checking stats
            try:
                stats = index.describe_index_stats()
                namespace_stats = stats.get('namespaces', {}).get(namespace, {})
                vector_count = namespace_stats.get('vector_count', 0)
                logger.info(f"Verification: Namespace {namespace} now has {vector_count} vectors")
                
                if vector_count == 0:
                    logger.warning(f"Warning: No vectors found immediately after upload in namespace {namespace}")
                    # Wait a bit more and check again
                    time.sleep(3)
                    stats = index.describe_index_stats()
                    namespace_stats = stats.get('namespaces', {}).get(namespace, {})
                    vector_count = namespace_stats.get('vector_count', 0)
                    logger.info(f"Second verification: Namespace {namespace} now has {vector_count} vectors")
                    
            except Exception as e:
                logger.warning(f"Could not verify vector storage: {e}")
            
            # Return a simple success indicator
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing vectors: {str(e)}")
            raise e
    
    def search_documents(self, query: str, namespace: str, k: int = 5) -> List:
        """Search for relevant documents from namespace"""
        try:
            if not self.embeddings or not self.pc:
                logger.error("Vector service not properly configured. Cannot search documents.")
                return []
            
            logger.info(f"Searching documents in namespace {namespace} with query: {query[:50]}...")
            
            # Create vectorstore from existing index
            vectorstore = LangchainPinecone.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace=namespace
            )
            
            # Search for similar documents
            results = vectorstore.similarity_search(query, k=k)
            
            logger.info(f"🔍 Found {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching documents: {str(e)}")
            return []
    
    def store_chat_message(self, message: str, namespace: str, metadata: dict):
        """Store chat message in vector database"""
        try:
            if not self.embeddings or not self.pc:
                logger.error("Vector service not properly configured. Cannot store chat message.")
                return None
                
            logger.info(f"Storing chat message in namespace: {namespace}")
            logger.info(f"Message preview: {message[:100]}...")
            
            # Add text to metadata for retrieval
            metadata['text'] = message
            
            vectorstore = LangchainPinecone.from_texts(
                texts=[message],
                embedding=self.embeddings,
                index_name=self.index_name,
                namespace=namespace,
                metadatas=[metadata]
            )
            
            logger.info(f"✅ Successfully stored chat message in namespace {namespace}")
            return vectorstore
            
        except Exception as e:
            logger.error(f"❌ Error storing chat message: {str(e)}")
            return None
    
    def search_similar_content(self, query: str, session_id: str, k: int = 5) -> List[str]:
        """Search for relevant content from user's documents"""
        try:
            # Create vectorstore from existing index
            vectorstore = LangchainPinecone.from_existing_index(
                index_name=self.index_name,
                embedding=self.embeddings,
                namespace=session_id
            )
            
            # Search for similar documents
            results = vectorstore.similarity_search(query, k=k)
            
            # Extract text content
            relevant_texts = [doc.page_content for doc in results]
            
            print(f"🔍 Found {len(relevant_texts)} relevant chunks for query")
            return relevant_texts
            
        except Exception as e:
            print(f"❌ Error searching documents: {str(e)}")
            return []
    
    def clear_session_data(self, session_id: str):
        """Clear all vectors for a specific session"""
        try:
            # In new Pinecone API, access index directly using the index name
            index = self.pc.Index(self.index_name)
            
            # Delete all vectors in the session namespace
            index.delete(delete_all=True, namespace=session_id)
            
            print(f"🗑️ Cleared all data for session {session_id}")
            
        except Exception as e:
            print(f"❌ Error clearing session data: {str(e)}")
    
    def get_session_stats(self, session_id: str) -> dict:
        """Get statistics for a session's stored documents"""
        try:
            index = self.pc.Index(self.index_name)
            stats = index.describe_index_stats()
            
            # Get namespace-specific stats
            namespace_stats = stats.get('namespaces', {}).get(session_id, {})
            
            return {
                'total_vectors': namespace_stats.get('vector_count', 0),
                'session_id': session_id
            }
            
        except Exception as e:
            print(f"❌ Error getting session stats: {str(e)}")
            return {'total_vectors': 0, 'session_id': session_id}
    
    def get_all_documents(self, namespace: str, k: int = 20) -> List:
        """Get all documents from namespace"""
        try:
            if not self.embeddings or not self.pc:
                logger.error("Vector service not properly configured. Cannot get documents.")
                return []
            
            # Get the index object
            index = self.pc.Index(self.index_name)
            
            logger.info(f"Attempting to retrieve documents from namespace {namespace}")
            
            # First, check namespace stats to see if any vectors exist
            max_retries = 3
            for retry in range(max_retries):
                try:
                    stats = index.describe_index_stats()
                    namespace_stats = stats.get('namespaces', {}).get(namespace, {})
                    vector_count = namespace_stats.get('vector_count', 0)
                    logger.info(f"Attempt {retry + 1}: Namespace {namespace} has {vector_count} vectors")
                    
                    if vector_count > 0:
                        break
                    elif retry < max_retries - 1:
                        logger.info(f"No vectors found, waiting 2 seconds before retry...")
                        import time
                        time.sleep(2)
                    else:
                        logger.warning(f"No vectors found in namespace {namespace} after {max_retries} attempts")
                        return []
                        
                except Exception as e:
                    logger.warning(f"Could not get namespace stats on attempt {retry + 1}: {e}")
                    if retry < max_retries - 1:
                        import time
                        time.sleep(2)
            
            # Try multiple approaches to retrieve documents
            documents = []
            
            # Approach 1: Try with a very generic query
            try:
                query_embedding = self.embeddings.embed_query("content text information")
                
                query_response = index.query(
                    vector=query_embedding,
                    top_k=k,
                    namespace=namespace,
                    include_metadata=True
                )
                
                logger.info(f"Query returned {len(query_response.matches)} matches")
                
                for match in query_response.matches:
                    if 'text' in match.metadata:
                        # Create a simple document object
                        doc = type('Document', (), {
                            'page_content': match.metadata['text'],
                            'metadata': match.metadata
                        })()
                        documents.append(doc)
                        
            except Exception as e:
                logger.warning(f"Query approach failed: {e}")
            
            # Approach 2: If no documents found, try using LangChain vectorstore
            if not documents:
                try:
                    logger.info("Trying LangChain vectorstore approach")
                    vectorstore = LangchainPinecone.from_existing_index(
                        index_name=self.index_name,
                        embedding=self.embeddings,
                        namespace=namespace
                    )
                    
                    # Try similarity search with generic terms
                    search_terms = ["information", "content", "text", "data", "document"]
                    for term in search_terms:
                        try:
                            results = vectorstore.similarity_search(term, k=k)
                            if results:
                                documents.extend(results)
                                logger.info(f"Found {len(results)} documents with search term '{term}'")
                                break
                        except Exception as e:
                            logger.warning(f"Search with term '{term}' failed: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"LangChain approach failed: {e}")
            
            logger.info(f"Retrieved {len(documents)} documents from namespace {namespace}")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            return []
    
    def get_chat_history(self, namespace: str, k: int = 50) -> List:
        """Get chat history from namespace - searches for individual messages"""
        try:
            if not self.embeddings or not self.pc:
                logger.error("Vector service not properly configured. Cannot get chat history.")
                return []
                
            logger.info(f"Getting chat history from namespace: {namespace}")
            
            # First check if namespace exists and has vectors
            try:
                index = self.pc.Index(self.index_name)
                stats = index.describe_index_stats()
                namespace_stats = stats.get('namespaces', {}).get(namespace, {})
                vector_count = namespace_stats.get('vector_count', 0)
                logger.info(f"Chat namespace {namespace} has {vector_count} vectors")
                
                if vector_count == 0:
                    logger.info(f"No chat messages found in namespace {namespace}")
                    return []
                    
            except Exception as e:
                logger.warning(f"Could not check namespace stats: {e}")
            
            # Try to use LangChain vectorstore to get chat history
            try:
                vectorstore = LangchainPinecone.from_existing_index(
                    index_name=self.index_name,
                    embedding=self.embeddings,
                    namespace=namespace
                )
                
                # Try different search strategies for individual messages
                docs = []
                
                # Strategy 1: Search for user messages
                user_docs = vectorstore.similarity_search("user message question", k=k//2)
                logger.info(f"Found {len(user_docs)} user message docs")
                docs.extend(user_docs)
                
                # Strategy 2: Search for assistant messages
                assistant_docs = vectorstore.similarity_search("assistant response answer", k=k//2)
                logger.info(f"Found {len(assistant_docs)} assistant message docs")
                docs.extend(assistant_docs)
                
                # Strategy 3: If no results, try broader search
                if not docs:
                    docs = vectorstore.similarity_search("message chat conversation", k=k)
                    logger.info(f"Found {len(docs)} docs with 'message chat conversation' search")
                
                # Strategy 4: Generic search to get any documents
                if not docs:
                    docs = vectorstore.similarity_search("", k=k)
                    logger.info(f"Found {len(docs)} docs with empty search")
                
                # Remove duplicates based on content
                seen_content = set()
                unique_docs = []
                for doc in docs:
                    content_hash = hash(doc.page_content)
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        unique_docs.append(doc)
                
                logger.info(f"Total unique chat history documents found: {len(unique_docs)}")
                return unique_docs
                
            except Exception as e:
                logger.error(f"Error using LangChain vectorstore for chat history: {str(e)}")
                return []
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def clear_namespace(self, namespace: str):
        """Clear all vectors from a namespace"""
        try:
            if not self.pc:
                logger.warning("Pinecone not configured. Cannot clear namespace.")
                return
                
            # Get the index directly from Pinecone
            index = self.pc.Index(self.index_name)
            index.delete(delete_all=True, namespace=namespace)
            logger.info(f"🗑️ Cleared namespace: {namespace}")
        except Exception as e:
            if "Namespace not found" not in str(e):
                logger.error(f"Error clearing namespace: {str(e)}")
                raise e

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from .vector_service import VectorService
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        try:
            self.vector_service = VectorService()
            
            # Initialize Google Gemini model
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                logger.warning("GOOGLE_API_KEY not found. Using fallback response mode.")
                self.model = None
            else:
                self.model = ChatGoogleGenerativeAI(
                    model="models/gemini-2.5-pro", 
                    temperature=0.7,
                    google_api_key=google_api_key
                )
                
        except Exception as e:
            logger.error(f"Error initializing AI Service: {str(e)}")
            self.model = None
            self.vector_service = None
        
    def get_qa_chain(self):
        """Get question-answering chain"""
        if not self.model:
            return None
            
        prompt_template = """
You are a helpful AI assistant. Use the following extracted context from the user's PDF documents to answer the question accurately and comprehensively.

Instructions:
- Base your answer primarily on the provided context
- If the context doesn't contain relevant information, politely mention that the information is not available in the uploaded PDFs
- Provide detailed, well-structured answers when possible
- Use markdown formatting for better readability
- Include specific details and examples from the context when relevant

Context from PDF documents:
{context}

User Question:
{question}

Detailed Answer:
"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        return load_qa_chain(self.model, chain_type="stuff", prompt=prompt)
    
    def get_information_extraction_chain(self):
        """Get information extraction chain for user data"""
        if not self.model:
            return None
            
        prompt_template = """
You are an expert information extraction specialist with extraordinary ability to find ALL technical skills and technologies mentioned ANYWHERE in a document. Your mission is to extract comprehensive user information with particular focus on technical skills that may be scattered throughout different sections.

EXTRACTION MISSION: Find EVERY single technical mention, no matter how brief or subtle.

## User Information

### Personal Details
• **Full Name:** [Extract the full name]
• **Email Address:** [Extract email address] 
• **Phone Number:** [Extract phone number]
• **Current Location:** [Extract current location/address]

### Professional Background
• **Years of Experience:** [Extract years of experience in their field]
• **Desired Position(s):** [Extract desired job positions/roles]
• **Current Role:** [Extract current job title/position if mentioned]

### Technical Skills & Technologies
**CRITICAL: Search the ENTIRE document for ANY technical mention. Include everything found in:**
- Skills sections
- Work experience descriptions
- Project descriptions
- Education and coursework
- Certifications
- Achievements
- Company names (if tech companies)
- Job titles (if technical roles)
- Research or publication topics
- Internship descriptions
- Extracurricular activities

• **Programming Languages:** [Extract ALL programming languages mentioned anywhere: Python, Java, JavaScript, C++, C#, SQL, HTML, CSS, etc.]
• **Frontend Technologies:** [React, Angular, Vue, jQuery, Bootstrap, TypeScript, etc.]
• **Backend Frameworks:** [Django, Flask, Spring, Express, Node.js, ASP.NET, etc.]
• **Databases & Data Technologies:** [MySQL, PostgreSQL, MongoDB, Redis, Oracle, SQLite, etc.]
• **Cloud Platforms & Services:** [AWS, Azure, GCP, Firebase, Heroku, specific services like EC2, S3, Lambda, etc.]
• **Development Tools & IDEs:** [Git, GitHub, Docker, VS Code, IntelliJ, Eclipse, Jenkins, etc.]
• **Operating Systems:** [Windows, Linux, macOS, Ubuntu, CentOS, etc.]
• **Web Technologies:** [REST APIs, GraphQL, AJAX, JSON, XML, WebSocket, etc.]
• **Machine Learning & AI:** [TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Keras, OpenCV, etc.]
• **DevOps & Infrastructure:** [Docker, Kubernetes, CI/CD, Jenkins, Terraform, Ansible, etc.]
• **Testing & Quality:** [Jest, Pytest, Selenium, JUnit, Cypress, Mocha, etc.]
• **Mobile Development:** [React Native, Flutter, Swift, Kotlin, Xamarin, Ionic, etc.]
• **Data & Analytics:** [Tableau, Power BI, Apache Spark, Hadoop, Elasticsearch, etc.]
• **Design & Graphics:** [Figma, Adobe Creative Suite, Sketch, Photoshop, Canva, etc.]
• **Project Management:** [Jira, Trello, Asana, Slack, Agile, Scrum, Kanban, etc.]
• **Other Technologies:** [ANY other technical tools, platforms, software, or technologies mentioned]

### COMPREHENSIVE SEARCH INSTRUCTIONS:
1. **Scan EVERY word** of the document for technical terms
2. **Include technologies mentioned in**:
   - Course names and subjects
   - Project titles and descriptions
   - Work responsibilities and achievements
   - Internship experiences
   - Research topics
   - Technical clubs or competitions
   - Software and tools used in any context
3. **Look for implicit technologies**:
   - If web development is mentioned, include HTML, CSS, JavaScript
   - If data science work, include Python, SQL, pandas, numpy
   - If mobile development, include relevant frameworks
4. **Include ALL variations**:
   - Full names and abbreviations (JavaScript and JS)
   - Version numbers if mentioned
   - Related technologies in the same domain

**CRITICAL**: If you find ANYTHING technical, include it. Better to include too much than miss important skills.

Instructions:
- If any information is not found, skip that field entirely rather than writing "Not mentioned"
- Be EXTREMELY thorough in extracting ALL technical mentions
- Include technologies even if mentioned very briefly
- Search every section multiple times
- Include everything that could be remotely technical
- Only include information that is actually present in the document

Document Content:
{context}

Extracted Information:
"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
        return load_qa_chain(self.model, chain_type="stuff", prompt=prompt)
    
    def get_technical_questions_chain(self):
        """Get technical questions generation chain"""
        if not self.model:
            return None
            
        prompt_template = """
You are an expert technical interviewer. Based on the provided tech stack and difficulty level, generate relevant technical interview questions.

Tech Stack: {tech_stack}
Difficulty Level: {difficulty}

Generate 8-12 technical questions based on the tech stack with the specified difficulty level:

**Instructions:**
- For "Easy": Focus on basic concepts, syntax, and fundamental understanding
- For "Medium": Include practical application, problem-solving, and intermediate concepts  
- For "Hard": Cover advanced topics, optimization, design patterns, and complex scenarios

**Format your response as:**

# Technical Interview Questions ({difficulty_upper} Level)

**Tech Stack Covered:** {tech_stack}

---

## Questions:

### 1. **Question 1:** [Your question here]
   *Topic: [Related technology/concept]*
   *Expected time: [X minutes]*

### 2. **Question 2:** [Your question here]  
   *Topic: [Related technology/concept]*
   *Expected time: [X minutes]*

### 3. **Question 3:** [Your question here]
   *Topic: [Related technology/concept]*
   *Expected time: [X minutes]*

[Continue for all questions...]

---

## Interview Tips:
- Allow candidates to think aloud and explain their reasoning
- Look for problem-solving approach, not just correct answers
- Be prepared with follow-up questions based on their responses

Please ensure questions are relevant, practical, and test both knowledge and application skills.

Generated Questions:
"""
        prompt = PromptTemplate(template=prompt_template, input_variables=["tech_stack", "difficulty", "difficulty_upper"])
        return prompt

    def extract_user_information(self, namespace: str) -> str:
        """Extract user information from uploaded documents with enhanced technical detection"""
        try:
            # Check if AI model is available
            if not self.model:
                return "ERROR: AI service is not properly configured. Please check your Google API key."
            
            if not self.vector_service:
                return "ERROR: Vector service is not properly configured. Please check your Pinecone settings."
            
            # Get all documents from the namespace with maximum chunks
            docs = self.vector_service.get_all_documents(namespace, k=50)
            
            if not docs:
                return "WARNING: No documents found to extract information from. Please upload a PDF document first."
            
            # Log the found documents for debugging
            logger.info(f"Found {len(docs)} document chunks for information extraction")
            
            # Combine all document content for better context
            combined_content = "\n\n".join([doc.page_content for doc in docs])
            
            # Enhanced extraction prompt with direct content injection
            extraction_prompt = f"""
You are an expert information extraction specialist. Extract comprehensive user information from this resume/document with MAXIMUM attention to technical skills scattered throughout ALL sections.

RESUME/DOCUMENT CONTENT:
{combined_content}

EXTRACTION REQUIREMENTS:

## User Information

### Personal Details
• **Full Name:** [Extract the full name]
• **Email Address:** [Extract email address] 
• **Phone Number:** [Extract phone number]
• **Current Location:** [Extract current location/address]

### Professional Background
• **Years of Experience:** [Extract years of experience in their field]
• **Desired Position(s):** [Extract desired job positions/roles]
• **Current Role:** [Extract current job title/position if mentioned]

### Technical Skills & Technologies
**CRITICAL MISSION: Find EVERY technical skill mentioned ANYWHERE in the document**

Scan ALL sections for technical content:
- Skills/Technical sections
- Work experience descriptions and responsibilities
- Project descriptions and technologies used
- Education courses and programming languages learned
- Certifications and technical training
- Achievements that mention technologies
- Research work and tools used
- Internship experiences
- Software and tools mentioned in any context

• **Programming Languages:** [PRIORITY 1: Find explicit "Programming Languages" sections and extract ALL items listed. Look for: C, C++, C/C++, Python, Java, JavaScript, TypeScript, etc.]

• **Frontend Technologies:** [React, Angular, Vue.js, jQuery, Bootstrap, HTML, CSS, JavaScript, TypeScript, etc.]

• **Backend Frameworks:** [Django, Flask, Spring, Express, Node.js, ASP.NET, etc.]

• **Libraries & Tools:** [NumPy, Pandas, Matplotlib, OpenCV, PyTorch, TensorFlow, Scikit-learn, etc.]

• **Development Tools & IDEs:** [Git, GitHub, Visual Studio, VS Code, IntelliJ, Eclipse, Jupyter, etc.]

• **Operating Systems & Platforms:** [Windows, Linux, macOS, Ubuntu, Jupyter, etc.]

• **Databases & Data Technologies:** [MySQL, PostgreSQL, MongoDB, Redis, SQL Server, etc.]

• **Cloud Platforms & Services:** [AWS, Microsoft Azure, Google Cloud Platform, Firebase, Heroku, Digital Ocean, specific services like EC2, S3, Lambda, etc.]

• **Development Tools & IDEs:** [Git, GitHub, GitLab, Docker, VS Code, IntelliJ IDEA, Eclipse, PyCharm, WebStorm, Jenkins, etc.]

• **Operating Systems:** [Linux, Ubuntu, CentOS, Windows, macOS, Unix, Red Hat, Debian, etc.]

• **Web Technologies:** [REST APIs, GraphQL, AJAX, JSON, XML, WebSocket, HTTP/HTTPS, OAuth, JWT, etc.]

• **Machine Learning & AI:** [TensorFlow, PyTorch, Scikit-learn, Keras, Pandas, NumPy, OpenCV, NLTK, spaCy, Jupyter, MLflow, etc.]

• **DevOps & Infrastructure:** [Docker, Kubernetes, Jenkins, CI/CD, GitLab CI/CD, GitHub Actions, Terraform, Ansible, etc.]

• **Testing & Quality:** [Jest, Pytest, JUnit, Selenium, Cypress, Mocha, Chai, TestNG, etc.]

• **Mobile Development:** [React Native, Flutter, Swift, Kotlin, Xamarin, Ionic, Cordova, etc.]

• **Data & Analytics:** [Tableau, Power BI, Apache Spark, Hadoop, Kafka, Apache Airflow, etc.]

• **Design & Graphics:** [Figma, Adobe Creative Suite, Sketch, Photoshop, Illustrator, Canva, etc.]

• **Project Management:** [Jira, Trello, Asana, Slack, Microsoft Teams, Agile, Scrum, Kanban, etc.]

• **Other Technologies:** [ANY other technical tools, platforms, software, libraries, frameworks mentioned]

### EXTRACTION STRATEGY:
1. **Read every word** of the document for technical terms
2. **Infer technologies** from job descriptions (e.g., "web developer" implies HTML, CSS, JavaScript)
3. **Extract from project contexts** - what technologies would be used for described projects
4. **Include coursework technologies** - programming languages and tools from education
5. **Company context inference** - if worked at tech companies, include likely technologies
6. **Version-aware extraction** - include version numbers when mentioned

**CRITICAL**: Extract EVERYTHING technical found. Better to include too much than miss important skills.

**Instructions:**
- If information not found, skip that field instead of writing "Not mentioned"
- Be EXTREMELY thorough in technical extraction
- Include technologies even if mentioned very briefly
- Infer common technologies from job contexts
- Search the entire document multiple times

**Extracted Information:**
"""
            
            # Use the model directly for more control
            result = self.model.invoke(extraction_prompt)
            
            # Extract the content from the result
            if hasattr(result, 'content'):
                output_text = result.content.strip()
            else:
                output_text = str(result).strip()
            
            if not output_text:
                output_text = "WARNING: Could not extract user information from the uploaded document."
            
            logger.info("Successfully extracted user information with enhanced technical detection")
            return output_text
            
        except Exception as e:
            logger.error(f"Information extraction error: {str(e)}")
            return f"I'm sorry, I encountered an error while extracting information. Error: {str(e)}"
    
    def generate_technical_questions(self, tech_stack: str, difficulty: str) -> str:
        """Generate technical questions based on tech stack and difficulty"""
        try:
            # Check if AI model is available
            if not self.model:
                return "ERROR: AI service is not properly configured. Please check your Google API key."
            
            # Validate difficulty level
            valid_difficulties = ["easy", "medium", "hard"]
            if difficulty.lower() not in valid_difficulties:
                return f"ERROR: Invalid difficulty level. Please choose from: {', '.join(valid_difficulties)}"
            
            # Get technical questions generation prompt
            prompt_template = self.get_technical_questions_chain()
            if not prompt_template:
                return "ERROR: Technical questions generation prompt could not be initialized."
            
            # Format the prompt with the tech stack and difficulty
            formatted_prompt = prompt_template.format(
                tech_stack=tech_stack,
                difficulty=difficulty.title(),
                difficulty_upper=difficulty.upper()
            )
            
            # Generate questions using the model directly
            result = self.model.invoke(formatted_prompt)
            
            # Extract the content from the result
            if hasattr(result, 'content'):
                output_text = result.content.strip()
            else:
                output_text = str(result).strip()
            
            if not output_text:
                output_text = f"WARNING: Could not generate technical questions for the provided tech stack and {difficulty} difficulty level."
            
            logger.info(f"Successfully generated {difficulty} technical questions for tech stack: {tech_stack[:50]}...")
            return output_text
            
        except Exception as e:
            logger.error(f"Technical questions generation error: {str(e)}")
            return f"I'm sorry, I encountered an error while generating technical questions. Error: {str(e)}"

    def extract_tech_stack_only(self, namespace: str) -> str:
        """Extract only the tech stack from uploaded documents with maximum aggression"""
        try:
            # Check if AI model is available
            if not self.model:
                return "ERROR: AI service is not properly configured. Please check your Google API key in the .env file."
            
            if not self.vector_service:
                return "ERROR: Vector service is not properly configured. Please check your Pinecone API key in the .env file."
            
            # Test vector service connection before proceeding
            try:
                # Get all documents from the namespace with maximum chunks
                docs = self.vector_service.get_all_documents(namespace, k=100)  # Even more chunks
            except Exception as vector_error:
                if "Unauthorized" in str(vector_error) or "Invalid API Key" in str(vector_error):
                    return "ERROR: Pinecone authentication failed. Please check your PINECONE_API_KEY in the .env file."
                elif "not found" in str(vector_error).lower():
                    return "ERROR: Pinecone index not found. Please check your Pinecone configuration."
                else:
                    return f"ERROR: Vector service error - {str(vector_error)}"
            
            if not docs:
                return "WARNING: No documents found to extract tech stack from. Please upload a PDF document first."
            
            # Combine all document content for better context
            combined_content = "\n\n".join([doc.page_content for doc in docs])
            
            # Ultra-aggressive tech stack extraction with explicit skills section focus
            tech_stack_prompt = f"""
EMERGENCY EXTRACTION MISSION: You are a forensic technical skill detector. Your job is to find EVERY SINGLE technical skill, technology, programming language, framework, tool, software, platform, methodology, or technical concept mentioned ANYWHERE in this document. MISSING EVEN ONE SKILL IS UNACCEPTABLE.

DOCUMENT CONTENT TO ANALYZE:
{combined_content}

CRITICAL EXTRACTION REQUIREMENTS:

1. SKILLS SECTIONS (HIGHEST PRIORITY):
   - Look for sections titled: "Skills", "Technical Skills", "Technologies", "Tools", "Programming Languages", "Frameworks", "Software", "Platforms"
   - Extract EVERY item listed in bullet points, lists, or comma-separated values
   - Pay special attention to explicitly listed skills

2. PROGRAMMING LANGUAGES:
   - Find ALL languages: C, C++, Python, Java, JavaScript, TypeScript, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB, SQL, HTML, CSS, etc.
   - Include variations: C/C++, Node.js, etc.

3. FRAMEWORKS & LIBRARIES:
   - React, Angular, Vue, Django, Flask, Spring, Express, TensorFlow, PyTorch, OpenCV, NumPy, Pandas, Matplotlib, Scikit-learn, etc.

4. TOOLS & PLATFORMS:
   - Git, GitHub, Docker, Kubernetes, Jenkins, VS Code, Visual Studio, IntelliJ, Eclipse, Jupyter, etc.

5. OPERATING SYSTEMS:
   - Windows, Linux, macOS, Ubuntu, CentOS, Unix, etc.

6. DATABASES:
   - MySQL, PostgreSQL, MongoDB, Redis, Oracle, SQL Server, SQLite, etc.

7. CLOUD PLATFORMS:
   - AWS, Azure, GCP, Firebase, Heroku, Digital Ocean, etc.

EXTRACTION INSTRUCTIONS:
- Read the document CHARACTER BY CHARACTER
- Extract EVERYTHING from skills sections first
- Look for both explicit lists AND contextual mentions
- Include technologies mentioned in project descriptions
- Include tools mentioned in work experience
- Include software mentioned in education
- When you see "Tools and Frameworks:", extract EVERYTHING after it
- When you see "Programming Languages:", extract EVERYTHING listed
- Include version numbers if mentioned
- Include both full names and abbreviations

ABSOLUTE REQUIREMENT: If you see explicit skill lists like:
"Programming Languages: C/C++, Python, JavaScript"
"Tools and Frameworks: React, Numpy, Pandas, Matplotlib, OpenCV, PyTorch, Tensorflow"
"Platforms: Jupyter, Visual Studio, Windows, Linux, Git"

YOU MUST EXTRACT EVERY SINGLE ITEM FROM THESE LISTS.

IMPORTANT: ONLY include technologies that are ACTUALLY MENTIONED in the document. DO NOT include placeholder text like "Not mentioned" or "N/A". If a technology is not found, simply don't include it in the output.

CRITICAL OUTPUT FORMAT: Return your findings as a SINGLE LINE of comma-separated technology names. Example format:
"Python, React, Node.js, Docker, AWS, PostgreSQL, Git, VS Code"

DO NOT use bullet points, numbering, or multiple lines. Just comma-separated technology names on one line.

COMPLETE TECHNOLOGY EXTRACTION:
"""
            
            # Use the model directly for more control
            result = self.model.invoke(tech_stack_prompt)
            
            # Extract the content from the result
            if hasattr(result, 'content'):
                tech_stack = result.content.strip()
            else:
                tech_stack = str(result).strip()
            
            # If the result seems incomplete, try a more targeted approach
            if not tech_stack or len(tech_stack) < 100:
                logger.warning("First extraction attempt yielded limited results, trying skills-focused approach")
                
                # Skills-focused extraction
                skills_focused_prompt = f"""
FOCUS ON EXPLICIT SKILLS SECTIONS:

Document:
{combined_content}

Find all sections that list technical skills, such as:
- "Technical Skills"
- "Programming Languages"  
- "Tools and Frameworks"
- "Platforms"
- "Software"

Extract EVERY technology mentioned in these sections. Look for lists, bullet points, and comma-separated items.

Also find technologies mentioned in:
- Work experience descriptions
- Project descriptions  
- Education/coursework

IMPORTANT: ONLY list technologies that are ACTUALLY MENTIONED in the document. Do not include "Not mentioned" or any placeholder text.

CRITICAL OUTPUT FORMAT: Return ONLY a single line of comma-separated technology names. Example:
"C/C++, Python, React, NumPy, PyTorch, Git, Linux"

DO NOT use bullet points, numbering, explanations, or multiple lines.

COMPLETE LIST OF ALL TECHNOLOGIES FOUND:
"""
                
                alternative_result = self.model.invoke(skills_focused_prompt)
                if hasattr(alternative_result, 'content'):
                    tech_stack = alternative_result.content.strip()
                else:
                    tech_stack = str(alternative_result).strip()
            
            # Clean up the response to remove "not mentioned" items
            tech_stack = self._clean_tech_stack_response(tech_stack)
            
            if not tech_stack:
                tech_stack = "No tech stack information found in the document."
            
            logger.info(f"Successfully extracted tech stack: {tech_stack[:200]}...")
            return tech_stack
            
        except Exception as e:
            logger.error(f"Tech stack extraction error: {str(e)}")
            return f"Error extracting tech stack: {str(e)}"

    def _clean_tech_stack_response(self, tech_stack: str) -> str:
        """Clean tech stack response to remove 'not mentioned' items and ensure comma-separated format"""
        if not tech_stack:
            return ""
        
        try:
            # Split by common delimiters - be more aggressive about parsing
            items = []
            
            # Handle different response formats - split by multiple delimiters
            if "\n" in tech_stack:
                # Split by newlines first
                items = tech_stack.split("\n")
            elif "," in tech_stack:
                items = tech_stack.split(",")
            elif ";" in tech_stack:
                items = tech_stack.split(";")
            else:
                items = [tech_stack]
            
            # Further split items that might contain commas
            all_items = []
            for item in items:
                if "," in item and "\n" not in item:
                    all_items.extend(item.split(","))
                else:
                    all_items.append(item)
            
            # Clean each item
            cleaned_items = []
            for item in all_items:
                # Clean whitespace and common formatting
                cleaned_item = item.strip()
                cleaned_item = cleaned_item.strip("- •*()[]{}\"'")  # Remove bullet points and brackets
                cleaned_item = cleaned_item.strip()
                
                # Skip empty items or "not mentioned" variations
                if not cleaned_item:
                    continue
                
                # Filter out "not mentioned" variations (case insensitive)
                lower_item = cleaned_item.lower()
                if any(phrase in lower_item for phrase in [
                    "not mentioned", 
                    "not found", 
                    "not specified", 
                    "not listed", 
                    "n/a", 
                    "none", 
                    "no specific",
                    "not explicitly",
                    "not detailed",
                    "complete list",
                    "technologies found",
                    "extraction"
                ]):
                    continue
                
                # Skip items that are just descriptions or explanations
                if len(cleaned_item) > 80:  # Likely a description, not a tech name
                    continue
                
                # Skip items that contain too many common words (likely explanations)
                common_words = ["the", "and", "or", "in", "on", "at", "to", "for", "with", "from", "that", "this", "are", "is"]
                word_count = sum(1 for word in common_words if word.lower() in lower_item)
                if word_count > 2:  # Likely a sentence, not a tech name
                    continue
                
                # Skip items that look like headers or labels
                if any(header in lower_item for header in [
                    "programming languages",
                    "frameworks",
                    "tools",
                    "platforms",
                    "databases",
                    "skills",
                    "technologies",
                    "software"
                ]) and len(cleaned_item.split()) < 4:
                    continue
                
                cleaned_items.append(cleaned_item)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_items = []
            for item in cleaned_items:
                item_lower = item.lower()
                if item_lower not in seen:
                    seen.add(item_lower)
                    unique_items.append(item)
            
            # Always return as comma-separated string
            result = ", ".join(unique_items) if unique_items else ""
            
            logger.info(f"Cleaned tech stack: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning tech stack response: {str(e)}")
            # Fallback: simple comma-separated conversion
            return ", ".join([item.strip() for item in tech_stack.split("\n") if item.strip() and "not mentioned" not in item.lower()])
            
            return result
            
        except Exception as e:
            logger.warning(f"Error cleaning tech stack response: {e}")
            return tech_stack  # Return original if cleaning fails
            result = self.model.invoke(tech_stack_prompt)
            
            # Extract the content from the result
            if hasattr(result, 'content'):
                tech_stack = result.content.strip()
            else:
                tech_stack = str(result).strip()
            
            # If the result seems incomplete, try a more targeted approach
            if not tech_stack or len(tech_stack) < 100:
                logger.warning("First extraction attempt yielded limited results, trying skills-focused approach")
                
                # Skills-focused extraction
                skills_focused_prompt = f"""
FOCUS ON EXPLICIT SKILLS SECTIONS:

Document:
{combined_content}

Find all sections that list technical skills, such as:
- "Technical Skills"
- "Programming Languages"  
- "Tools and Frameworks"
- "Platforms"
- "Software"

Extract EVERY technology mentioned in these sections. Look for lists, bullet points, and comma-separated items.

Also find technologies mentioned in:
- Work experience descriptions
- Project descriptions  
- Education/coursework

COMPLETE LIST OF ALL TECHNOLOGIES:
"""
                
                alternative_result = self.model.invoke(skills_focused_prompt)
                if hasattr(alternative_result, 'content'):
                    tech_stack = alternative_result.content.strip()
                else:
                    tech_stack = str(alternative_result).strip()
            
            if not tech_stack:
                tech_stack = "No tech stack information found in the document."
            
            logger.info(f"Successfully extracted tech stack: {tech_stack[:200]}...")
            return tech_stack
            
        except Exception as e:
            logger.error(f"Tech stack extraction error: {str(e)}")
            return f"Error extracting tech stack: {str(e)}"

    def ask_question(self, question: str, namespace: str) -> str:
        """Ask a question about the documents with fallback to general reasoning"""
        try:
            # Check if AI model is available
            if not self.model:
                return "ERROR: AI service is not properly configured. Please check your Google API key."
            
            if not self.vector_service:
                return "ERROR: Vector service is not properly configured. Please check your Pinecone settings."
            
            # Search for relevant documents
            docs = self.vector_service.search_documents(question, namespace, k=5)
            
            if docs and len(docs) > 0:
                # Found relevant documents - use document-based answering
                logger.info(f"Found {len(docs)} relevant document chunks for question: {question[:50]}...")
                
                # Get answer from AI based on documents
                chain = self.get_qa_chain()
                if not chain:
                    return "ERROR: AI chain could not be initialized. Please check your configuration."
                
                result = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
                output_text = result.get("output_text", "").strip()
                
                if output_text:
                    # Format the response nicely
                    formatted_response = f"""## Answer based on your documents:

{output_text}

---
*Note: This answer is based on the content from your uploaded PDF documents.*"""
                    logger.info(f"Successfully generated document-based answer for: {question[:50]}...")
                    return formatted_response
            
            # No relevant documents found or empty response - use general AI reasoning
            logger.info(f"No relevant documents found, using general AI reasoning for: {question[:50]}...")
            
            general_prompt = f"""You are a helpful AI assistant. The user has asked a question but no relevant information was found in their uploaded documents. Please provide a helpful, general answer based on your knowledge.

User Question: {question}

Please provide a comprehensive and helpful answer. If this is a technical question, provide examples and best practices. If it's a general question, provide useful information and context.

Format your response in a clear, organized manner with appropriate sections if needed."""

            # Use the model directly for general reasoning
            response = self.model.invoke(general_prompt)
            
            # Format the general response
            formatted_response = f"""## General AI Response:

{response.content if hasattr(response, 'content') else str(response)}

---
*Note: This is a general AI response since no relevant information was found in your uploaded documents. Consider uploading documents related to your question for more specific answers.*"""
            
            logger.info(f"Successfully generated general AI answer for: {question[:50]}...")
            return formatted_response
            
        except Exception as e:
            logger.error(f"AI Service error: {str(e)}")
            return f"""ERROR: Error Processing Question

I encountered an error while processing your question. Please try again.

**Error Details:** {str(e)}

**Troubleshooting Tips:**
• Check your internet connection
• Try rephrasing your question
• Ensure your documents are properly uploaded"""
    
    def ask_question_original(self, question: str, user_id: str, session_id: str, chat_namespace: str, doc_namespace: str) -> str:
        """Ask a question about the documents (original method)"""
        try:
            # Search for relevant documents
            docs = self.vector_service.search_documents(question, doc_namespace, k=5)
            
            if not docs:
                return "WARNING: No relevant content found in the uploaded PDFs to answer this question."
            
            # Get answer from AI
            chain = self.get_qa_chain()
            result = chain({"input_documents": docs, "question": question}, return_only_outputs=True)
            output_text = result.get("output_text", "").strip()
            
            if not output_text:
                output_text = "WARNING: The model couldn't generate an answer. Try rephrasing your question or check PDF content."
            
            # Store user question and AI response as separate messages in chat history
            import uuid
            
            # Generate unique message IDs
            question_id = str(uuid.uuid4())
            response_id = str(uuid.uuid4())
            
            question_metadata = {
                "user_id": user_id,
                "session_id": session_id,
                "type": "user_message",
                "role": "user",
                "message_id": question_id,
                "timestamp": datetime.now().isoformat()
            }
            print(f"Storing user question in namespace: {chat_namespace}")
            print(f"Question ID: {question_id}, Content: {question}")
            self.vector_service.store_chat_message(question, chat_namespace, question_metadata)
            
            # Store AI response
            response_metadata = {
                "user_id": user_id,
                "session_id": session_id,
                "type": "assistant_message",
                "role": "assistant",
                "message_id": response_id,
                "related_question_id": question_id,  # Link response to question
                "timestamp": datetime.now().isoformat()
            }
            print(f"Storing AI response in namespace: {chat_namespace}")
            print(f"Response ID: {response_id}, Content: {output_text[:100]}...")
            self.vector_service.store_chat_message(output_text, chat_namespace, response_metadata)
            
            return output_text
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return f"ERROR: Error while processing question: {str(e)}"
    
    def summarize_documents(self, user_id: str, session_id: str, doc_namespace: str) -> str:
        """Summarize all documents in the session"""
        try:
            docs = self.vector_service.get_all_documents(doc_namespace, k=20)
            
            if not docs:
                return "No documents found to summarize."
            
            chain = self.get_summarization_chain()
            response = chain({"input_documents": docs}, return_only_outputs=True)
            
            return response["output_text"]
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return f"ERROR: Error while summarizing: {str(e)}"

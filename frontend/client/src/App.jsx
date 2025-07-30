import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import AuthComponent from './AuthComponent';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [userId, setUserId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [documentsUploaded, setDocumentsUploaded] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [historyData, setHistoryData] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [showHistoryView, setShowHistoryView] = useState(false);
  const [selectedHistorySession, setSelectedHistorySession] = useState(null);
  const messagesEndRef = useRef(null);

  // Check if user is already logged in
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUsername = localStorage.getItem('username');
    const savedUserId = localStorage.getItem('userId');
    
    if (savedToken && savedUsername && savedUserId) {
      setCurrentUser(savedUsername);
      setUserId(savedUserId);
      setIsAuthenticated(true);
      
      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
    }
  }, []);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('userId');
    delete axios.defaults.headers.common['Authorization'];
    
    setCurrentUser(null);
    setUserId(null);
    setIsAuthenticated(false);
    setSessionId(null);
    setMessages([]);
    setDocumentsUploaded(false);
    setSelectedFiles([]);
    setHistoryData([]);
    setSessions([]);
    setShowHistoryView(false);
  }, []);

  const createSession = useCallback(async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/sessions/create`, {
        user_id: userId,
        session_name: 'New Chat Session'
      });
      setSessionId(response.data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
      if (error.response?.status === 401) {
        handleLogout();
        alert('Session expired. Please login again.');
      }
    }
  }, [userId, handleLogout]);

  // Create session when authenticated
  useEffect(() => {
    if (isAuthenticated && userId && !sessionId) {
      createSession();
    }
  }, [isAuthenticated, userId, sessionId, createSession]);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatMessageContent = (content) => {
    if (!content) return content;
    
    // Enhanced formatting for better readability
    let formatted = content
      // Handle markdown headers
      .replace(/^### (.*$)/gim, '<h3 class="content-header-h3">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="content-header-h2">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="content-header-h1">$1</h1>')
      
      // Handle bold text (**text**)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // Handle italic text (*text*)
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      // Handle code blocks
      .replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>')
      
      // Handle inline code
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      
      // Handle bullet points and lists
      .replace(/^\s*[-•]\s*(.+)$/gm, '<li class="bullet-item">$1</li>')
      
      // Handle numbered lists
      .replace(/^\s*(\d+\.)\s*(.+)$/gm, '<li class="numbered-item"><strong>$1</strong> $2</li>')
      
      // Wrap consecutive list items in ul tags
      .replace(/(<li class="bullet-item">.*?<\/li>)\s*(?=<li class="bullet-item">|$)/gs, (match) => {
        return match.includes('<ul>') ? match : '<ul class="bullet-list">' + match;
      })
      .replace(/(<ul class="bullet-list">.*?)(?=<\/li>\s*(?!<li))/gs, '$1</ul>')
      
      // Handle tables (basic markdown table support)
      .replace(/\|(.+)\|/g, (match, content) => {
        const cells = content.split('|').map(cell => cell.trim());
        const cellElements = cells.map(cell => `<td class="table-cell">${cell}</td>`).join('');
        return `<tr class="table-row">${cellElements}</tr>`;
      })
      
      // Wrap table rows
      .replace(/(<tr class="table-row">.*?<\/tr>\s*)+/gs, '<table class="content-table">$&</table>')
      
      // Handle line breaks
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>')
      
      // Handle special formatting for technical content
      .replace(/ERROR:/g, '<span class="error-text">ERROR:</span>')
      .replace(/WARNING:/g, '<span class="warning-text">WARNING:</span>')
      .replace(/Note:/g, '<span class="note-text">Note:</span>')
      
      // Clean up excessive breaks
      .replace(/(<br>){3,}/g, '<br><br>');

    // Wrap orphaned list items
    formatted = formatted.replace(/(<li class="bullet-item">(?:(?!<\/ul>).)*<\/li>)(?!\s*<\/ul>)/gs, '<ul class="bullet-list">$1</ul>');
    formatted = formatted.replace(/(<li class="numbered-item">(?:(?!<\/ol>).)*<\/li>)(?!\s*<\/ol>)/gs, '<ol class="numbered-list">$1</ol>');
    
    return formatted;
  };

  const handleLogin = (accessToken, username, user_id) => {
    setCurrentUser(username);
    setUserId(user_id);
    setIsAuthenticated(true);
    
    // Save to localStorage
    localStorage.setItem('token', accessToken);
    localStorage.setItem('username', username);
    localStorage.setItem('userId', user_id);
    
    // Set default authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  };

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Please select only PDF files');
      return;
    }
    
    setSelectedFiles(pdfFiles);
  };

  const uploadDocuments = async () => {
    if (!selectedFiles.length) {
      alert('Please select PDF files to upload');
      return;
    }

    if (!userId || !sessionId) {
      alert('User session not found. Please refresh the page.');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('user_id', userId);
    formData.append('session_id', sessionId);

    try {
      const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setDocumentsUploaded(true);
      alert('Documents uploaded successfully!');
      setSelectedFiles([]);
      
    } catch (error) {
      console.error('Upload failed:', error);
      if (error.response?.status === 401) {
        handleLogout();
        alert('Session expired. Please login again.');
      } else {
        alert(error.response?.data?.error || 'Upload failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;
    if (!documentsUploaded) {
      alert('Please upload documents first');
      return;
    }

    if (!userId || !sessionId) {
      alert('User session not found. Please refresh the page.');
      return;
    }

    const userMessage = {
      role: 'user',
      content: question,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentQuestion = question;
    setQuestion('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/ask`, {
        question: currentQuestion,
        user_id: userId,
        session_id: sessionId
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Failed to get answer:', error);
      if (error.response?.status === 401) {
        handleLogout();
        alert('Session expired. Please login again.');
      } else {
        const errorMessage = {
          role: 'assistant',
          content: error.response?.data?.error || 'Failed to get answer',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const clearSession = async () => {
    try {
      await axios.post(`${API_BASE_URL}/documents/clear`, {
        user_id: userId,
        session_id: sessionId
      });
      setMessages([]);
      setDocumentsUploaded(false);
      setSelectedFiles([]);
      alert('Session cleared successfully!');
    } catch (error) {
      console.error('Failed to clear session:', error);
      if (error.response?.status === 401) {
        handleLogout();
        alert('Session expired. Please login again.');
      } else {
        alert(error.response?.data?.error || 'Failed to clear session');
      }
    }
  };

  // History functions
  const fetchUserSessions = async () => {
    if (!userId) return;
    
    setIsLoadingHistory(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/history/sessions?user_id=${userId}`);
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      setSessions([]);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const fetchChatHistory = async (sessionId = null) => {
    if (!userId) return;
    
    setIsLoadingHistory(true);
    try {
      const url = sessionId 
        ? `${API_BASE_URL}/history/chat?user_id=${userId}&session_id=${sessionId}`
        : `${API_BASE_URL}/history/chat?user_id=${userId}`;
      
      const response = await axios.get(url);
      setHistoryData(response.data.history || []);
      
      if (sessionId) {
        setSelectedHistorySession(sessionId);
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
      setHistoryData([]);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const toggleHistoryView = () => {
    setShowHistoryView(!showHistoryView);
    if (!showHistoryView) {
      fetchUserSessions();
    }
  };

  const handleSessionCardClick = (sessionId) => {
    fetchChatHistory(sessionId);
  };

  const extractUserInfo = async () => {
    if (!documentsUploaded) {
      alert('Please upload documents first');
      return;
    }

    if (!userId || !sessionId) {
      alert('User session not found. Please refresh the page.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/extract/user-info`, {
        user_id: userId,
        session_id: sessionId
      });

      const extractedInfo = {
        role: 'assistant',
        content: `**Extracted User Information:**\n\n${response.data.extracted_info}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, extractedInfo]);
      
    } catch (error) {
      console.error('Failed to extract user info:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Failed to extract user information from the uploaded documents.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateQuestions = async (difficulty = 'medium') => {
    if (!documentsUploaded) {
      alert('Please upload documents first');
      return;
    }

    if (!userId || !sessionId) {
      alert('User session not found. Please refresh the page.');
      return;
    }

    setIsLoading(true);
    try {
      // First extract tech stack
      const techStackResponse = await axios.post(`${API_BASE_URL}/extract/tech-stack`, {
        user_id: userId,
        session_id: sessionId
      });

      const techStack = techStackResponse.data.tech_stack;
      
      if (!techStack || techStack.includes('No tech stack')) {
        const noTechMessage = {
          role: 'assistant',
          content: 'No technical skills found in the uploaded documents. Please upload a resume with technical skills listed.',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, noTechMessage]);
        return;
      }

      // Ask user for difficulty level
      const selectedDifficulty = prompt('Select difficulty level:\n- easy\n- medium\n- hard\n\nEnter your choice:', difficulty) || difficulty;

      // Generate questions based on tech stack
      const questionsResponse = await axios.post(`${API_BASE_URL}/questions/generate`, {
        tech_stack: techStack,
        difficulty: selectedDifficulty.toLowerCase()
      });

      // Format tech stack as comma-separated values - be aggressive about cleaning
      const formattedTechStack = techStack
        .split(/[\n,;]/)  // Split by newlines, commas, or semicolons
        .map(tech => tech.trim())
        .map(tech => tech.replace(/^[-•*]\s*/, ''))  // Remove bullet points
        .filter(tech => tech && tech.length > 0)
        .filter(tech => !tech.toLowerCase().includes('not mentioned'))
        .filter(tech => !tech.toLowerCase().includes('not found'))
        .filter(tech => !tech.toLowerCase().includes('not specified'))
        .filter(tech => tech.length < 50)  // Filter out descriptions
        .filter(tech => !tech.toLowerCase().includes('complete list'))
        .filter(tech => !tech.toLowerCase().includes('technologies found'))
        .join(', ');

      const questionsMessage = {
        role: 'assistant',
        content: `**Technical Questions (${selectedDifficulty.toUpperCase()} Level)**\n\n**Tech Stack Found:** ${formattedTechStack}\n\n${questionsResponse.data.questions}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, questionsMessage]);
      
    } catch (error) {
      console.error('Failed to generate questions:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Failed to generate technical questions. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const newSession = () => {
    setMessages([]);
    setDocumentsUploaded(false);
    setSelectedFiles([]);
    createSession();
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  // Show authentication component if not logged in
  if (!isAuthenticated) {
    return <AuthComponent onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Technical Question Generator</h1>
        <div className="user-info">
          <span>Welcome, {currentUser}</span>
          {!sessionId && (
            <button onClick={createSession} className="btn btn-primary" style={{marginRight: '10px'}}>
              Create Session
            </button>
          )}
          <button onClick={handleLogout} className="btn btn-secondary logout-btn">
            Logout
          </button>
        </div>
      </header>

      <div className="app-container">
        {/* Sidebar */}
        <div className="sidebar">
          <div className="section">
            <h3> Document Management</h3>
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileSelect}
              className="file-input"
            />
            {selectedFiles.length > 0 && (
              <div className="selected-files">
                <p>{selectedFiles.length} file(s) selected:</p>
                <ul>
                  {selectedFiles.map((file, index) => (
                    <li key={index}>{file.name}</li>
                  ))}
                </ul>
              </div>
            )}
            <button 
              onClick={uploadDocuments} 
              disabled={isLoading || !selectedFiles.length}
              className="btn btn-primary"
            >
               Upload & Process
            </button>
          </div>

          <div className="section">
            <h3> Actions</h3>
            <div className="action-buttons">
              <button 
                onClick={extractUserInfo} 
                disabled={isLoading || !documentsUploaded}
                className="btn btn-primary"
              >
                 Extract User Info
              </button>
              <button 
                onClick={() => generateQuestions('medium')} 
                disabled={isLoading || !documentsUploaded}
                className="btn btn-primary"
              >
                 Generate Questions
              </button>
              <button 
                onClick={toggleHistoryView} 
                disabled={isLoading || isLoadingHistory}
                className="btn btn-info"
              >
                {isLoadingHistory ? ' Loading...' : (showHistoryView ? ' Chat View' : ' History View')}
              </button>
              <button 
                onClick={clearSession} 
                disabled={isLoading}
                className="btn btn-danger"
              >
                 Clear Data
              </button>
              <button 
                onClick={newSession} 
                disabled={isLoading}
                className="btn btn-secondary"
              >
                 New Session
              </button>
            </div>
          </div>

          <div className="session-info">
            <small>
              User: {currentUser}
            </small>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="main-content">
          {showHistoryView ? (
            // History View
            <div className="history-container">
              <div className="history-header">
                <button onClick={toggleHistoryView} className="btn btn-secondary back-btn">
                  ← Back to Chat
                </button>
                <h2> Chat History</h2>
                <p>View your previous chat sessions</p>
              </div>
              
              {isLoadingHistory ? (
                <div className="loading-indicator">
                  <p> Loading history...</p>
                </div>
              ) : (
                <>
                  {/* Sessions List */}
                  <div className="sessions-grid">
                    <h3>Your Sessions</h3>
                    {sessions.length === 0 ? (
                      <p>No sessions found. Start chatting to create history!</p>
                    ) : (
                      <div className="session-cards">
                        {sessions.map((session, index) => (
                          <div 
                            key={session.session_id || index} 
                            className="session-card"
                            onClick={() => handleSessionCardClick(session.session_id)}
                          >
                            <div className="session-card-header">
                              <h4> {session.title || `Session ${index + 1}`}</h4>
                              <span className="session-id">ID: {session.session_id || 'Unknown'}</span>
                            </div>
                            <div className="session-card-body">
                              <p className="session-date">
                                Created: {session.created_at ? new Date(session.created_at).toLocaleDateString() : 'Unknown'}
                              </p>
                              <p className="session-docs">
                                Documents: {session.document_count || 0}
                              </p>
                            </div>
                            <div className="session-card-footer">
                              <span className="click-hint">Click to view history</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Selected Session History */}
                  {selectedHistorySession && historyData.length > 0 && (
                    <div className="session-history">
                      <h3> Chat History for Session: {selectedHistorySession.substring(0, 8)}...</h3>
                      <div className="history-messages">
                        {historyData.map((item, index) => (
                          <div key={index} className="history-message-pair">
                            <div className="history-question">
                              <div className="message-header">
                                <span className="role-badge user">👤 You</span>
                                <span className="timestamp">
                                  {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Unknown time'}
                                </span>
                              </div>
                              <div className="message-content">
                                {item.question}
                              </div>
                            </div>
                            <div className="history-answer">
                              <div className="message-header">
                                <span className="role-badge assistant"> Assistant</span>
                              </div>
                              <div className="message-content" dangerouslySetInnerHTML={{
                                __html: formatMessageContent(item.answer)
                              }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedHistorySession && historyData.length === 0 && (
                    <div className="no-history">
                      <p>No chat history found for this session.</p>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            // Regular Chat View
            <div className="chat-container">
              <div className="messages">
                {messages.length === 0 ? (
                  <div className="empty-state">
                    <p>Upload Resume or CV</p>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div key={index} className={`message ${message.role} ${message.session_id && message.session_id !== sessionId ? 'historical' : ''}`}>
                      <div className="message-content">
                        {message.session_id && message.session_id !== sessionId && (
                          <div className="session-indicator">
                             From Session: {message.session_short}
                          </div>
                        )}
                        <div 
                          className="message-text"
                          dangerouslySetInnerHTML={{
                            __html: message.role === 'assistant' 
                              ? formatMessageContent(message.content)
                              : message.content
                          }}
                        />
                        <div className="message-timestamp">
                          {new Date(message.timestamp).toLocaleTimeString()}
                          {message.session_id && message.session_id !== sessionId && (
                            <span className="session-badge"> • Previous Session</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="message assistant">
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="input-area">
                <div className="input-container">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={documentsUploaded ? "Ask a question " : "Please upload documents first"}
                    disabled={!documentsUploaded || isLoading}
                    rows="3"
                    className="question-input"
                  />
                  <button 
                    onClick={askQuestion}
                    disabled={!question.trim() || !documentsUploaded || isLoading}
                    className="btn btn-primary send-btn"
                  >
                    Send 
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

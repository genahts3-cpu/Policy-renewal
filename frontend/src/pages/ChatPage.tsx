import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, PlusCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { sendChat } from '../api/services'
import { useAuthStore } from '../store/authStore'
import { Button } from '../components/ui/Button'
import type { ChatMessage } from '../types'

const SUGGESTED = [
  'What does my health insurance cover?',
  'When does my auto policy expire?',
  'Should I renew my life insurance?',
  'What is my deductible?',
  'How do I file a claim?',
  'What are my coverage limits?',
]

const INITIAL_MESSAGE: ChatMessage = {
  role: 'assistant',
  content: "Hello! I'm your AI insurance assistant. I can help you understand your policies, answer questions, and provide renewal recommendations. How can I help you today?",
  timestamp: new Date().toISOString(),
}

const getChatKey = (suffix: string) => {
  const uid = localStorage.getItem('customer_id') ?? 'guest'
  return `chat_${uid}_${suffix}`
}

export function ChatPage() {
  const { isAdmin } = useAuthStore()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = sessionStorage.getItem(getChatKey('messages'))
    return saved ? JSON.parse(saved) : [INITIAL_MESSAGE]
  })
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | undefined>(
    () => sessionStorage.getItem(getChatKey('session_id')) || undefined
  )
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isAdmin) navigate('/admin', { replace: true })
  }, [isAdmin, navigate])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    sessionStorage.setItem(getChatKey('messages'), JSON.stringify(messages))
  }, [messages])

  useEffect(() => {
    if (sessionId) sessionStorage.setItem(getChatKey('session_id'), sessionId)
  }, [sessionId])

  const newChat = () => {
    sessionStorage.removeItem(getChatKey('messages'))
    sessionStorage.removeItem(getChatKey('session_id'))
    setMessages([{ ...INITIAL_MESSAGE, timestamp: new Date().toISOString() }])
    setSessionId(undefined)
    setInput('')
  }

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return
    const userMsg: ChatMessage = { role: 'user', content: text, timestamp: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await sendChat(text, sessionId)
      setSessionId(res.session_id)
      const aiMsg: ChatMessage = {
        role: 'assistant',
        content: res.response,
        intent: res.intent,
        sources: res.sources,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.', timestamp: new Date().toISOString() },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-6 py-4 flex items-center gap-3">
        <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-semibold text-gray-900">AI Insurance Assistant</h1>
          <p className="text-xs text-gray-500">Powered by LangGraph + GPT-4o</p>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <button
            onClick={newChat}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors font-medium"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            New Chat
          </button>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs text-gray-500">Online</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-100'
            }`}>
              {msg.role === 'user'
                ? <User className="w-4 h-4 text-white" />
                : <Bot className="w-4 h-4 text-gray-600" />
              }
            </div>
            <div className={`max-w-[75%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
              <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-sm'
                  : 'bg-white border border-gray-100 text-gray-800 rounded-tl-sm shadow-sm'
              }`}>
                {msg.content}
              </div>
              {msg.intent && msg.intent !== 'general_chat' && msg.intent !== 'off_topic' && msg.intent !== 'blocked' && (
                <span className="text-xs text-gray-400 px-1">Intent: {msg.intent.replace(/_/g, ' ')}</span>
              )}
              {msg.sources && msg.sources.length > 0 && (
                <div className="flex flex-wrap gap-1 px-1">
                  {msg.sources.map((s, si) => (
                    <span key={si} className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                      📄 {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
              <Bot className="w-4 h-4 text-gray-600" />
            </div>
            <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
              <div className="flex gap-1 items-center">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="px-6 pb-2">
          <p className="text-xs text-gray-400 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="text-xs px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-100 p-4">
        <div className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage(input)}
            placeholder="Ask about your policies, renewals, coverage..."
            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <Button onClick={() => sendMessage(input)} disabled={!input.trim() || loading} size="lg">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

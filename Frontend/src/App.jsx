
import React, { useState } from "react";
import {
  Send, Scissors, Star, Moon, Sun, Menu, X, MessageCircle,
  Sparkles, Calendar, Hand, Heart, Gift, Zap, Lightbulb
} from "lucide-react";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: `Welcome to the Beauty & Aesthetics AI Agent Suite 🌸
I'm your intelligent assistant for beauty salons and aesthetic clinics.
Ask me to find top-rated spas, book appointments, or get personalized beauty recommendations!`,
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState("");
  const [isDark, setIsDark] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loyaltyPoints] = useState(850);

//   const VITE_YELP_API_URL = "http://127.0.0.1:5000";
  const VITE_YELP_API_URL = "http://localhost:5000"

  // Helper function to extract location from user input
  const extractLocation = (query) => {
    const locationPatterns = [
      /in ([a-zA-Z\s]+?)(?:\?|$|,|\.|near|for)/i,
      /at ([a-zA-Z\s]+?)(?:\?|$|,|\.|near|for)/i,
      /near ([a-zA-Z\s]+?)(?:\?|$|,|\.|in|for)/i,
      /around ([a-zA-Z\s]+?)(?:\?|$|,|\.|near|for)/i,
      /([a-zA-Z\s]+?)(?:,\s*[A-Z]{2})/,  // City, ST format
    ];

    for (const pattern of locationPatterns) {
      const match = query.match(pattern);
      if (match && match[1]) {
        return match[1].trim();
      }
    }

    // Default location if none found
    return 'New York';
  };

  // Helper function to extract search term from user input
  const extractSearchTerm = (query) => {
    const beautyKeywords = [
      'salon', 'spa', 'beauty', 'hair', 'facial', 'manicure', 'pedicure',
      'massage', 'wax', 'makeup', 'nail', 'aesthetic', 'skin care',
      'barbershop', 'hairdresser', 'cosmetologist', 'beautician', 'stylist'
    ];

    const lowerQuery = query.toLowerCase();
    const matchedKeyword = beautyKeywords.find(keyword => lowerQuery.includes(keyword));

    if (matchedKeyword) {
      return matchedKeyword;
    }

    // If no keyword found, use first few words
    const words = query.split(/\s+/).slice(0, 3).join(' ');
    return words || 'beauty salon';
  };


const handleSend = async () => {
  if (!input.trim()) return;

  const userMessage = { role: "user", content: input, timestamp: new Date() };
  setMessages((prev) => [...prev, userMessage]);
  setInput("");
  setIsLoading(true);

  try {
    // Dynamically send query to unified endpoint
    const response = await fetch(`${VITE_YELP_API_URL}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userMessage.content }),
    });

    if (!response.ok) throw new Error(`HTTP error! ${response.status}`);
    const data = await response.json();

    // 🧩 Dynamically handle backend response types
    let aiMessage = {
      role: "assistant",
      content: "",
      timestamp: new Date(),
    };

    if (data.type === "rag" && data.answer) {
      // RAG system (e.g., Botox/Evolus product info)
      aiMessage.content = `💡 **Product Knowledge Response:**\n${data.answer}`;
    } else if (data.type === "business" && data.results?.length) {
      // Yelp-style business search results
      const formatted = data.results
        .map(
          (r, i) =>
            `${i + 1}. ${r.name} (${r.rating}⭐)\n📍 ${r.address}\n📞 ${r.phone}\n🔗 ${r.url}`
        )
        .join("\n\n");

      aiMessage.content = `💅 **Here are some beauty & spa options I found:**\n\n${formatted}`;
    } else if (data.answer) {
      // Fallback for generic answers
      aiMessage.content = data.answer;
    } else {
      aiMessage.content =
        "🤔 I couldn’t find a clear answer. Try rephrasing or specifying a location!";
    }

    setMessages((prev) => [...prev, aiMessage]);
  } catch (error) {
    console.error("Backend error:", error);
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content:
          "⚠️ Unable to reach the backend. Please ensure your Flask server is running at http://localhost:5000.",
        timestamp: new Date(),
      },
    ]);
  } finally {
    setIsLoading(false);
  }
};


  // 🧭 Quick user actions
  const handleQuickAction = (action) => {
    let query = "";
    switch (action) {
      case "book":
        query = "I’d like to book a beauty appointment.";
        break;
      case "view":
        query = "Show me my upcoming appointments.";
        break;
      case "recommend":
        query = "Can you recommend a beauty treatment for me?";
        break;
      case "services":
        query = "What services does your salon offer?";
        break;
      default:
        query = "Tell me more about your services.";
    }
    setInput(query);
  };

  const handleRedeemRewards = () => {
    alert("🎉 Rewards redeemed successfully! You’ve unlocked a free facial treatment.");
  };

  // 🖌️ Theme
  const bgClass = isDark ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900";
  const cardClass = isDark ? "bg-gray-800 border-gray-700" : "bg-white border-gray-200";
  const mutedText = isDark ? "text-gray-400" : "text-gray-600";

  return (
    <div className={`min-h-screen ${bgClass} transition-all`}>
      {/* Header */}
      <header className="bg-gradient-to-r from-pink-600 via-rose-500 to-purple-600 py-4 shadow-lg relative overflow-hidden">
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_30%_20%,white,transparent_70%)]"></div>
        <div className="relative z-10 max-w-6xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center border border-white/30">
              <Scissors className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                Beauty & Aesthetics AI Agent Suite
              </h1>
              <p className="text-sm text-white/80 font-light">
                An intelligent, multi-agent platform for salons & aesthetic clinics ✨
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setIsDark(!isDark)}
              className="p-2 rounded-lg bg-white/10 border border-white/30 text-white hover:bg-white/20 transition-all"
            >
              {isDark ? <Sun className="w-5 h-5 text-yellow-300" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-lg bg-white/10 border border-white/30 text-white hover:bg-white/20 transition-all"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-12 bg-gradient-to-br from-blue-50 via-pink-50 to-purple-50 dark:from-gray-800 dark:via-gray-900 dark:to-gray-900">
        <div className="absolute top-0 left-0 w-96 h-96 bg-pink-200 rounded-full blur-3xl opacity-10 animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-purple-300 rounded-full blur-3xl opacity-10 animate-pulse"></div>

        <div className="relative z-10 max-w-6xl mx-auto px-6">
          {/* Main Heading */}
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 bg-clip-text text-transparent leading-relaxed max-w-4xl mx-auto">
              The Beauty & Aesthetics AI Agent Suite integrates conversational AI to manage appointment scheduling,
              client interactions, and personalized recommendations.
            </h2>
          </div>

          {/* Three Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {/* Clients Card */}
            <div className="p-5 rounded-xl shadow-md bg-gradient-to-br from-pink-500 to-rose-600 text-white">
              <div className="flex items-center gap-2 mb-3">
                <Heart className="w-5 h-5" />
                <h3 className="text-base font-semibold">Clients</h3>
              </div>
              <p className="text-pink-50 text-xs leading-relaxed">
                Seamless booking and personalized AI insights.
              </p>
            </div>

            {/* Rewards Card */}
            <div className={`p-5 rounded-xl shadow-md border ${cardClass}`}>
              <div className="flex items-center gap-2 mb-3">
                <Gift className="w-5 h-5 text-yellow-500" />
                <h3 className="text-base font-semibold">Your Rewards</h3>
              </div>
              <p className={`text-xs mb-3 ${mutedText}`}>🪙 Points: {loyaltyPoints}</p>
              <button
                onClick={handleRedeemRewards}
                className="w-full px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs font-semibold rounded-lg shadow-sm hover:opacity-90 transition-all">
                🎉 Redeem
              </button>
            </div>

            {/* Staff Card */}
            <div className="p-5 rounded-xl shadow-md bg-gradient-to-br from-purple-500 to-indigo-600 text-white">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-yellow-200" />
                <h3 className="text-base font-semibold">Staff & Management</h3>
              </div>
              <p className="text-purple-50 text-xs leading-relaxed">
                Streamline operations and business intelligence.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content - Side by Side Layout */}
      <section className="max-w-6xl mx-auto px-6 py-10">
        <div className="flex flex-col lg:flex-row gap-6">

          {/* Left Side - Quick Actions */}
          <aside className="lg:w-80 flex-shrink-0">
            <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <MessageCircle className="w-6 h-6 text-pink-500" /> Quick Actions
            </h3>

            <div className="flex flex-col gap-4">
              <button onClick={() => handleQuickAction("book")}
                className="p-5 rounded-lg bg-gradient-to-r from-pink-500 to-rose-500 text-white font-semibold hover:opacity-90 transition-all shadow-md text-left">
                💅 Book an Appointment
              </button>
              <button onClick={() => handleQuickAction("view")}
                className="p-5 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-semibold hover:opacity-90 transition-all shadow-md text-left">
                📅 View My Appointments
              </button>
              <button onClick={() => handleQuickAction("recommend")}
                className="p-5 rounded-lg bg-gradient-to-r from-purple-500 to-fuchsia-500 text-white font-semibold hover:opacity-90 transition-all shadow-md text-left">
                💡 Get Treatment Recommendations
              </button>
              <button onClick={() => handleQuickAction("services")}
                className="p-5 rounded-lg bg-gradient-to-r from-emerald-500 to-green-500 text-white font-semibold hover:opacity-90 transition-all shadow-md text-left">
                💬 Ask About Services
              </button>
            </div>
          </aside>

          {/* Right Side - Messages */}
          <main className="flex-1 flex flex-col gap-4">
            <h3 className="text-2xl font-bold flex items-center gap-2">
              <MessageCircle className="w-6 h-6 text-blue-500" /> Messages
            </h3>

            <div className={`flex-1 rounded-xl border shadow-md p-6 ${cardClass}`}>
              <div className="space-y-4 max-h-[60vh] overflow-y-auto">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`p-4 max-w-[80%] rounded-lg shadow-sm ${
                        msg.role === "user"
                          ? "bg-blue-600 text-white"
                          : isDark
                            ? "bg-gray-700 text-gray-100"
                            : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-line leading-relaxed">{msg.content}</p>
                      <span className={`text-xs block mt-2 ${isDark ? "text-gray-400" : "text-gray-500"}`}>
                        {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="p-3 rounded-lg bg-gray-600 text-gray-100 animate-pulse">
                      Searching for top-rated salons near you... 💆‍♀️
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Input Area */}
            <div className={`rounded-xl border p-4 shadow-md flex gap-3 ${cardClass}`}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask about spas, facials, or clinics near you..."
                className={`flex-1 px-4 py-3 rounded-lg border focus:ring-2 focus:ring-blue-500 ${
                  isDark ? "bg-gray-700 text-white border-gray-600" : "bg-white text-gray-900 border-gray-300"
                }`}
              />
              <button
                onClick={handleSend}
                className="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white font-semibold flex items-center gap-2 transition-all shadow-sm"
              >
                <Send className="w-5 h-5" />
                Send
              </button>
            </div>
          </main>

        </div>
      </section>
    </div>
  );
}



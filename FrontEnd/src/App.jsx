import { useState } from "react";

export default function SafeContent() {
  const [level, setLevel] = useState("level1");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // 🔊 SPEAK
  const speak = (text) => {
    speechSynthesis.cancel();

    const chunks = text.match(/.{1,150}/g) || [];

    chunks.forEach((chunk) => {
      const utterance = new SpeechSynthesisUtterance(chunk);
      utterance.lang = "he-IL";
      speechSynthesis.speak(utterance);
    });
  };

  const stopSpeech = () => {
    speechSynthesis.cancel();
  };

  // 🔥 ANALYZE
  const handleAnalyze = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), level }),
      });

      if (!response.ok) throw new Error("Request failed");

      const data = await response.json();
      setResult(data);

      // 🔊 AUTO READ
      const fullText = [
        data.title,
        ...(data.sections?.map(s => `${s.subtitle || ""} ${s.content}`) || [])
      ].join(". ");

      speak(fullText);

    } catch (err) {
      setError("שגיאה בניתוח הקישור. נסה שוב.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gradient-to-br from-slate-100 via-white to-slate-200 text-right">

      {/* NAVBAR */}
      <header className="fixed top-0 w-full backdrop-blur-xl bg-white/70 border-b border-slate-200 z-50 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <h1 className="text-xl font-extrabold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            SafeContent
          </h1>

          <div className="flex gap-2 bg-white/60 p-1 rounded-full shadow-inner">
            {["level1", "level2"].map((m) => (
              <button
                key={m}
                onClick={() => setLevel(m)}
                className={`px-4 py-2 rounded-full text-sm ${
                  level === m
                    ? "bg-purple-500 text-white"
                    : "text-slate-600"
                }`}
              >
                {m === "level1" ? "פגיעה קשה רמה 1" : "פגיעה קשה רמה 2"}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* MAIN */}
      <main className="pt-28 pb-16 px-4 flex justify-center">
        <div className="w-full max-w-2xl">

          {/* HERO */}
          <div className="text-center mb-12">
            <h2 className="text-4xl font-extrabold text-slate-800 mb-3">
              ניתוח תוכן בטוח
            </h2>
          </div>

          {/* INPUT */}
          <div className="flex gap-3 mb-10">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="הכנס קישור..."
              className="flex-1 px-5 py-4 rounded-2xl bg-white border"
            />

            <button
              onClick={handleAnalyze}
              disabled={loading || !url.trim()}
              className="px-6 py-4 bg-purple-500 text-white rounded-2xl"
            >
              {loading ? "טוען..." : "נתח"}
            </button>
          </div>

          {/* ERROR */}
          {error && <div className="text-red-500">{error}</div>}

          {/* RESULT */}
          {result && (
            <div className="space-y-6">

              {/* AUDIO */}
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    const fullText = [
                      result.title,
                      ...(result.sections?.map(s => `${s.subtitle || ""} ${s.content}`) || [])
                    ].join(". ");
                    speak(fullText);
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded-xl"
                >
                  🔊 נגן
                </button>

                <button
                  onClick={stopSpeech}
                  className="px-4 py-2 bg-red-500 text-white rounded-xl"
                >
                  ⛔ עצור
                </button>
              </div>

              {/* TITLE */}
              <h3 className="text-2xl font-bold">{result.title}</h3>

              {/* SECTIONS */}
              {result.sections?.map((section, i) => (
                <div key={i}>
                  <h4 className="font-semibold">{section.subtitle}</h4>
                  <p>{section.content}</p>
                </div>
              ))}

            </div>
          )}

        </div>
      </main>
    </div>
  );
}
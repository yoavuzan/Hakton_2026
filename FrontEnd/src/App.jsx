import { useState } from "react";

export default function SafeContent() {
  const [level, setLevel] = useState("level1");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [result, setResult] = useState({ title: "", sections: [] });
  const [error, setError] = useState(null);

  const isPTSD = level === "level1";

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

  // 🔥 ANALYZE (STREAMING)
  const handleAnalyze = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setResult({ title: "", sections: [] });
    setError(null);
    setStatus("מתחיל ניתוח...");

    try {
      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), disability: level }),
      });

      if (!response.ok) throw new Error("הקשר עם השרת נכשל");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const chunk = JSON.parse(line);

            // 🔹 STATUS
            if (chunk.type === "status") {
              setStatus(chunk.message);
            }

            // 🔹 STREAM DATA
            if (chunk.type === "data") {
              setResult((prev) => {
                const newSections = [...prev.sections];
                const incoming = chunk.chunk.sections || [];

                incoming.forEach((section, i) => {
                  if (newSections[i]) {
                    newSections[i] = {
                      subtitle: section.subtitle || newSections[i].subtitle,
                      content: section.content || newSections[i].content,
                    };
                  } else {
                    newSections[i] = {
                      subtitle: section.subtitle || "",
                      content: section.content || "",
                    };
                  }
                });

                return {
                  title: chunk.chunk.title || prev.title,
                  sections: newSections,
                };
              });
            }

            // 🔹 END
            if (chunk.type === "end") {
              setLoading(false);
              setStatus("הניתוח הושלם");

              // 🔊 AUTO SPEAK
              setTimeout(() => {
                const fullText = [
                  result.title,
                  ...result.sections.map(
                    (s) => `${s.subtitle || ""} ${s.content}`
                  ),
                ].join(". ");

                speak(fullText);
              }, 300);
            }

            // 🔹 ERROR
            if (chunk.type === "error") {
              throw new Error(chunk.message);
            }

          } catch (e) {
            console.error("Parse error:", e);
          }
        }
      }

    } catch (err) {
      console.error("Request error:", err);
      setError(err.message);
      setLoading(false);
      setStatus("");
    }
  };
  const isSevere = level === "level1";

return (
  <div
    dir="rtl"
    className={`
      min-h-screen
      bg-gradient-to-br from-slate-100 via-white to-slate-200
      font-sans
      text-right
      ${isSevere ? "text-[22px] leading-[2]" : "text-[16px] leading-relaxed"}
    `}
  >
    {/* NAVBAR */}
    <header
      className={`
        fixed top-0 w-full border-b z-50 shadow-sm
        ${isSevere ? "bg-white" : "backdrop-blur-xl bg-white/70"}
      `}
    >
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <h1 className="text-xl font-extrabold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
          SafeContent
        </h1>

        <div className="flex gap-2 bg-white/60 p-1 rounded-full">
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
              {m === "level1" ? "פגיעה קשה" : "פגיעה קלה"}
            </button>
          ))}
        </div>
      </div>
    </header>

    {/* MAIN */}
    <main className="pt-28 pb-16 px-4 flex justify-center">
      <div className="w-full max-w-xl mx-auto">

        {/* TITLE */}
        <h2
          className={`
            font-bold text-center mb-6 text-slate-700
            ${isSevere ? "text-3xl leading-loose" : "text-xl"}
          `}
        >
          ניתוח תוכן בטוח
        </h2>

        {/* INPUT */}
        <div className="flex gap-3 mb-10">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && handleAnalyze()}
            placeholder="הכנס קישור לניתוח..."
            className="flex-1 px-5 py-4 rounded-2xl border shadow-sm focus:ring-2 focus:ring-purple-300 text-[16px]"
          />

          <button
            onClick={handleAnalyze}
            disabled={loading || !url.trim()}
            className={`px-6 py-4 rounded-2xl font-bold ${
              loading
                ? "bg-slate-200 text-slate-400"
                : "bg-purple-500 hover:bg-purple-600 text-white"
            }`}
          >
            {loading ? "טוען..." : "נתח"}
          </button>
        </div>

        {/* LOADING */}
        {loading && (
          <div className="text-center py-10 text-slate-600">
            {status}
          </div>
        )}

        {/* ERROR */}
        {error && (
          <div className="text-red-500 text-center mb-4">
            {error}
          </div>
        )}

        {/* RESULT */}
        {(result.title || result.sections.length > 0) && (
          <div className={isSevere ? "space-y-8" : "space-y-5"}>

            {/* AUDIO */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  const fullText = [
                    result.title,
                    ...result.sections.map(
                      (s) => `${s.subtitle || ""} ${s.content}`
                    ),
                  ].join(". ");
                  speak(fullText);
                }}
                className="px-4 py-2 bg-blue-500 text-white rounded-xl"
              >
                🔊 האזנה
              </button>

              <button
                onClick={stopSpeech}
                className="px-4 py-2 bg-red-500 text-white rounded-xl"
              >
                ⛔ הפסק האזנה
              </button>
            </div>

            {/* TITLE */}
            <h3
              className={`
                font-bold text-slate-900
                ${isSevere ? "text-3xl mb-6" : "text-xl mb-3"}
              `}
            >
              {result.title}
            </h3>

            {/* SECTIONS */}
            {result.sections.map((section, i) => (
                <div
                    key={i}
                    className={`
                  bg-white
                  border border-slate-200
                  rounded-2xl
                  shadow-sm
                  ${isSevere ? "p-8 space-y-5" : "p-5 space-y-3"}
                `}
                >
                  {section.subtitle && (
                      <h4
                          className={`
                      font-bold border-b border-slate-200 pb-2
                      ${isSevere ? "text-xl" : "text-base"}
                    `}
                      >
                        {section.subtitle}
                      </h4>
                  )}

                  <p
                      className={`
                        text-slate-900
                        whitespace-pre-line
                        bg-slate-50 rounded-lg
                        ${isSevere
                        ? "text-[22px] leading-[2] p-5"
                         : "text-[16px] leading-relaxed p-3"}
                      `}
                                      >
                    {section.content}
                  </p>
              </div>
              ))}
          </div>
          )}

      </div>
    </main>
  </div>
);
}
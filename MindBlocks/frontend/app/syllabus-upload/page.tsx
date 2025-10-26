"use client";
import { useEffect, useState } from "react";
import { useSession } from "../context/SessionContext";
import { useRouter } from "next/navigation";

interface PlannedEvent {
  title: string;
  description: string;
  start: string;
  end: string;
  topics: string[];
}

export default function SyllabusUploadPage() {
  const { user, loading } = useSession();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [rawText, setRawText] = useState("");
  const [plannedEvents, setPlannedEvents] = useState<PlannedEvent[]>([]);
  const [loadingSchedule, setLoadingSchedule] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.push("/");
  }, [loading, user, router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
  };

  const generateSchedule = async () => {
    if (!file && !rawText) return alert("Upload a PDF or paste syllabus text");
    setLoadingSchedule(true);
    try {
      const formData = new FormData();
      if (file) formData.append("file", file);

      const res = await fetch("https://mindblocks-backend.onrender.com/schedule/generate", {
        method: "POST",
        credentials: "include",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setPlannedEvents(data.planned_events || []);
      } else {
        alert("Failed to generate schedule");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingSchedule(false);
    }
  };

  const createCalendarEvents = async () => {
    try {
        console.log(plannedEvents)
      const res = await fetch("https://mindblocks-backend.onrender.com/schedule/create", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ planned_events: plannedEvents }),
      });
      if (res.ok) {
        alert("Events created in Google Calendar!");
        const data = await res.json()
        console.log(data)
    }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading || !user) return <div>Loading...</div>;

  return (
    // <div style={{ padding: 40 }}>
    //   <h1>Upload Syllabus & Generate Schedule</h1>

    //   <div style={{ marginTop: 20 }}>
    //     <input type="file" accept="application/pdf" onChange={handleFileChange} />
    //   </div>
    //   <div style={{ marginTop: 20 }}>
    //     <textarea
    //       placeholder="Or paste syllabus text here"
    //       value={rawText}
    //       onChange={(e) => setRawText(e.target.value)}
    //       style={{ width: "100%", height: 120 }}
    //     />
    //   </div>

    //   <button
    //     onClick={generateSchedule}
    //     disabled={loadingSchedule}
    //     style={{ marginTop: 20, padding: "10px 20px" }}
    //   >
    //     {loadingSchedule ? "Generating..." : "Generate Schedule"}
    //   </button>

    //   {plannedEvents.length > 0 && (
    //     <div style={{ marginTop: 30 }}>
    //       <h2>Planned Study Blocks</h2>
    //       <ul>
    //         {plannedEvents.map((ev, i) => (
    //           <li key={i}>
    //             <strong>{ev.title}</strong> ({new Date(ev.start).toLocaleString()} -{" "}
    //             {new Date(ev.end).toLocaleString()})<br />
    //             Topics: {ev.topics.join(", ")}
    //           </li>
    //         ))}
    //       </ul>
    //       <button onClick={createCalendarEvents} style={{ marginTop: 20, padding: "10px 20px" }}>
    //         Add to Google Calendar
    //       </button>
    //     </div>
    //   )}
    // </div>
     <div className="min-h-screen bg-white text-black p-8">
      {/* Header */}
      <h1 className="text-4xl font-bold text-center mb-10">
        <span className="text-blue-400">Upload Syllabus</span> & <span className="text-pink-400">Generate Schedule</span>
      </h1>

      {/* Upload Section */}
      <div className="max-w-2xl mx-auto bg-zinc-900 rounded-2xl shadow-lg p-6 space-y-6">
        {/* File Upload */}
        <div>
          <label className="block text-white text-lg font-semibold mb-2">Upload PDF</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:bg-blue-400 file:text-black
              hover:file:bg-blue-500 cursor-pointer"
          />
        </div>

        {/* Raw Text Area */}
        {/* Need to implement this later */}
        {/* <div>
          <label className="block text-white text-lg font-semibold mb-2">Or Paste Text</label>
          <textarea
            placeholder="Paste syllabus text here..."
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            className="w-full h-40 rounded-xl p-4 text-black bg-white focus:outline-none focus:ring-2 focus:ring-pink-400"
          />
        </div> */}

        {/* Generate Button */}
        <button
          onClick={generateSchedule}
          disabled={loadingSchedule}
          className="w-full bg-pink-400 hover:bg-pink-500 text-black font-semibold py-3 rounded-xl transition disabled:opacity-50"
        >
          {loadingSchedule ? "Generating..." : "Generate Schedule"}
        </button>
      </div>

      {/* Planned Events Section */}
      {plannedEvents.length > 0 && (
        <div className="max-w-3xl mx-auto mt-12">
          <h2 className="text-2xl font-bold mb-6 text-center text-blue-400">
            Planned Study Blocks
          </h2>
          <ul className="space-y-4">
            {plannedEvents.map((ev, i) => (
              <li
                key={i}
                className="bg-zinc-900 rounded-xl p-4 shadow-md hover:shadow-lg transition"
              >
                <strong className="text-pink-400">{ev.title}</strong>
                <p className="text-sm text-gray-300 mt-1">
                  {new Date(ev.start).toLocaleString()} –{" "}
                  {new Date(ev.end).toLocaleString()}
                </p>
                <p className="mt-2 text-gray-200">
                  <span className="font-semibold">Topics:</span> {ev.topics.join(", ")}
                </p>
              </li>
            ))}
          </ul>

          <button
            onClick={createCalendarEvents}
            className="mt-8 w-full bg-blue-400 hover:bg-blue-500 text-black font-semibold py-3 rounded-xl transition"
          >
            Add to Google Calendar
          </button>
        </div>
      )}
    </div>
  );
}

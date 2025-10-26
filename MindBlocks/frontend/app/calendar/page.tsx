"use client";
import { Calendar, Clock } from "lucide-react";
import { Calendar as BigCalendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "./calendar.css"; // custom overrides

const localizer = momentLocalizer(moment);
import { useEffect, useState } from "react";
import { useSession } from "../context/SessionContext";
import { useRouter } from "next/navigation";

interface GoogleEvent {
  summary: string;
  start: { dateTime?: string; date?: string };
  end: { dateTime?: string; date?: string };
}

export default function CalendarPage() {
  const { user, loading } = useSession();
  const [events, setEvents] = useState<GoogleEvent[]>([]);
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/"); // redirect if not logged in
    }
  }, [loading, user, router]);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch("https://mindblocks-backend.onrender.com/calendar/events", {
          credentials: "include", // send HttpOnly JWT cookie
        });
        if (res.ok) {
          const data = await res.json();
          setEvents(data.events || []);
        }
      } catch (err) {
        console.error("Failed to fetch calendar events", err);
      }
    };
    if (user) fetchEvents();
  }, [user]);

  if (loading || !user) return <div>Loading...</div>;

  return (
    
     <div className="min-h-screen bg-white text-black p-8">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-10">
        <h1 className="text-4xl font-bold">
          <span className=" text-pink-400">{user.full_name}'s</span> Calendar
        </h1>
        <Calendar className="w-10 h-10 text-pink-400" />
      </div>

      {/* No Events */}
      {events.length === 0 && (
        <div className="text-center text-gray-400 mt-20">
          <p className="text-xl">No events found</p>
          <p className="mt-2">Start planning your schedule!</p>
        </div>
      )}

      {/* Events Grid */}
      {events.length > 0 && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {events.map((e, i) => (
            <div
              key={i}
              className="bg-blue-400 text-black rounded-2xl p-6 shadow-lg hover:scale-105 transition"
            >
              <h2 className="text-xl font-bold mb-2">{e.summary || "Untitled Event"}</h2>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-5 h-5" />
                <span>
                  {e.start?.dateTime
                    ? new Date(e.start.dateTime).toLocaleString()
                    : "No start time"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>

     
  );
  
}

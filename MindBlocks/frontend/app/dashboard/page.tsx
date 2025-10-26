"use client";
import { useEffect } from "react";
import { useSession } from "../context/SessionContext";
import { useRouter } from "next/navigation";
import { CalendarDays, Clock } from "lucide-react";
import Link from "next/link";


export default function DashboardPage() {
  const { user, loading } = useSession();
  const router = useRouter();
const handleLogout = async () => {
  try {
    await fetch("https://mindblocks-backend.onrender.com/auth/logout", {
      method: "GET",
      credentials: "include",
    });
    router.push("/"); // redirect frontend manually
  } catch (err) {
    console.error("Logout failed:", err);
  }
};

  useEffect(() => {
    if (!loading && !user) {
      router.push("/"); // redirect if not logged in
    }
  }, [loading, user, router]);

  if (loading || !user) return <div>Loading...</div>;

  return (
    <div className="min-h-screen p-8">
  {/* Header */}
  <div className="flex justify-between items-center mb-12">
    <h1 className="text-6xl font-bold">
      Welcome, <span className="text-pink-400">{user.full_name}</span>
    </h1>
    <div className="flex items-center gap-4">
      <img
        src={user.picture}
        alt="Profile"
        className="w-16 h-16 rounded-full border-4 border-blue-400 shadow-md"
      />
      <button
        onClick={handleLogout}
        className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-xl text-lg font-semibold transition"
      >
        Logout
      </button>
    </div>
  </div>

  {/* Action Cards */}
      <div className="grid gap-8 max-w-3xl mx-auto">
        {/* Current Events Card */}
        <div className="bg-blue-400 text-white rounded-2xl shadow-lg p-6 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <CalendarDays className="w-10 h-10" />
            <h2 className="text-2xl font-bold">Your Current Events</h2>
          </div>
          <p className="text-lg">
            See all your scheduled events, tasks, and deadlines in one place.
          </p>
          <Link href='/calendar'><button className="self-start bg-black text-white px-6 py-2 rounded-xl hover:bg-gray-800 transition">
            View Events
          </button></Link>
        </div>

        {/* Work Blocks Card */}
        <div className="bg-pink-400 text-white rounded-2xl shadow-lg p-6 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <Clock className="w-10 h-10" />
            <h2 className="text-2xl font-bold">Plan Work Blocks</h2>
          </div>
          <p className="text-lg">
            Break down your day into productive work sessions to stay focused.
          </p>
          <Link href='/syllabus-upload'><button className="self-start bg-black text-white px-6 py-2 rounded-xl hover:bg-gray-800 transition">
            Plan Blocks
          </button></Link>
        </div>
      </div>


</div>

  );
}

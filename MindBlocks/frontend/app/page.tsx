import Link from "next/link";
import Image from "next/image";
import TypingText from "@/components/ui/shadcn-io/typing-text";



export default function HomePage() {
  return (
    <div>
      <div className="p-12 flex min-h-screen flex-col justify-center items-center gap-8">
      <h1 className="text-8xl">Welcome To <span className="text-pink-400">Mind</span><span className="text-blue-400">Blocks</span></h1>
      <TypingText
        text={[ "An AI Study Schedule Planner", "To stop planning and focus on studying!"]}
        typingSpeed={75}
        pauseDuration={1500}
        showCursor={true}
        cursorCharacter="|"
        className="text-6xl text-center font-bold"
        textColors={[ '#f38aea', '#3ba2ff']}
        variableSpeed={{ min: 50, max: 120 }}
/>
      
      <a
        href="https://mindblocks-backend.onrender.com/auth/google"
        className=" mt-12 text-2xl rounded-sm bg-black h-fit p-4 flex w-fit justify-center items-center text-white border-r-2 no-underline"
        
      >
        Sign in with Google
      </a>
    </div>


      {/* the section on ai planning the schedule */}
    <div className="flex min-h-screen m-12">
      
      <div className="w-1/2">
        <Image alt="A picture of a lady holding a calendar event." width={1} height={1} className="w-fit" src="/calendar.svg"/>
      </div>
      <div className="w-1/2 p-12 flex-col justify-center items-top">
        <p className="text-6xl text-blue-400 mb-8">
          Dynamic Planning
          </p>
        <p className="text-3xl">
          MindBlocks utilizes AI to plan all your study sessions for you with a simple upload of a syllabus. Conveniently integrating these workblocks into your already planned events on Google Calendar. 
        </p>
      </div>

    </div>

    <div className="flex m-12">
      
      
      <div className="w-1/2 p-12 flex-col justify-center items-top">
        <p className="text-6xl text-pink-400 mb-8">
          Focus on studying
          </p>
        <p className="text-3xl">
          MindBlocks helps you save time by creating a perfect plan so that you can focus on studying rather than planning.
        </p>
      </div>

      <div className="w-1/3 ml-auto">
        <Image alt="A picture of a lady working next to a giant clock representing time management." width={1} height={1} className="w-fit" src="/time.svg"/>
      </div>

    </div>

    <footer className="bg-white text-2xl rounded-lg  ">
    <div className="w-full max-w-screen-xl mx-auto p-4 md:py-8">
        <div className="sm:flex sm:items-center sm:justify-between">
            <a href="/" className="flex items-center mb-4 sm:mb-0 space-x-3 rtl:space-x-reverse">
                <img src="/logo.png" className="h-16" alt="MindBlocks Logo" />
                <span className="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">MindBlocks</span>
            </a>
            <ul className="flex flex-wrap items-center mb-2 text-lg font-medium text-gray-500 sm:mb-0 dark:text-gray-400">
                <li>
                    <a href="/" className="hover:underline me-4 md:me-6">About</a>
                </li>
                <li>
                    <a href="/privacy" className="hover:underline me-4 md:me-6">Privacy Policy</a>
                </li>
              
                <li>
                    <a target="_blank" href="https://nanditarajkumar.vercel.app" className="hover:underline">Contact</a>
                </li>
            </ul>
        </div>
        
        <span className="block text-lg text-gray-500 sm:text-center dark:text-gray-400">© 2025 <a href="/" className="hover:underline">MindBlocks™</a>. All Rights Reserved.</span>
    </div>
</footer>


    </div>
    
  );
}

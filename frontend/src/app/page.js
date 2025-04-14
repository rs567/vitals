export default function Home() {
  return (
    <div className="bg-black h-screen p-10">
      <div className="h-full flex">
        <div className="flex-1/4 bg-white p-8 pr-4">
          <div className="h-full p-8 bg-gray-600 flex flex-col gap-4">
            <div className="basis-2/3 bg-gray-400">1</div>
            <div className="basis-2/3 bg-gray-400">2</div>
            <div className="basis-3/3 bg-gray-400">3</div>
          </div>
        </div>
        <div className="flex-3/4 bg-white p-8 pl-4">
          <div className="h-full p-8 bg-gray-600 flex flex-col gap-4">
            <div className="basis-3/7 bg-gray-400">
              <div>5</div>
            </div>
            <div className="basis-4/7 bg-inherit flex gap-4">
              <div className="basis-1/3 bg-gray-400">6</div>
              <div className="basis-2/3 bg-gray-400">7</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

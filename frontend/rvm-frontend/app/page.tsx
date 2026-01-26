import Image from "next/image";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center font-sans">
      <main className="flex min-h-screen w-full max-w-3xl flex-col p-8 bg-gray-200 gap-3">
        <div className="flex flex-row justify-center gap-3">
          <div className="flex rounded-4xl bg-[#3B9549] px-6 pt-10 overflow-hidden w-[25vh] h-[35vh]">
            <div className="flex rounded-t-3xl justify-center pt-6 pb-4 bg-[#114e1a] w-full h-full">
              <Image
                src="/images/Bottle.png"
                alt="Bottle"
                width={200}
                height={200}
                className="object-contain"
              />
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-2">
          <div className="flex flex-col text-[#114E1A] text-center border-2 p-3 rounded-3xl justify-center gap-2">
            <h2 className="font-bold">PUT BOTTLE INSIDE COMPARTMENT</h2>
            <hr />
            <p className="text-xs">One bottle at a time</p>
          </div>

          <div className="flex flex-col text-[#114E1A] text-center border-2 p-3 rounded-3xl ustify-center gap-2">
            <p className="text-[3vh] font-medium">
              Note: Only 500ml plastic bottles are accepted
            </p>
            <p className="text-[2vh]">Property of Green Module Systems</p>
          </div>
        </div>

        <a
          href=""
          className="flex items-center justify-center w-full p-4 bg-[#078C10] rounded-4xl"
        >
          <h1 className="font-extrabold text-xl">SCAN BOTTLE</h1>
        </a>
      </main>
    </div>
  );
}

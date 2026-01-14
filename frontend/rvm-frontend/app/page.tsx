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
                width={150}
                height={200}
                className="object-contain"
              />
            </div>
          </div>

          <div className="flex flex-col text-[#114E1A] text-center border-2 p-3 rounded-3xl w-[25vh] h-[35vh] justify-center gap-4">
            <h1 className="font-bold">PUT BOTTLE INSIDE COMPARTMENT</h1>
            <hr />
            <p className="text-xs">Ibutang ang botilya sa suludlan</p>
          </div>
        </div>

        <div className="flex items-center justify-center w-full p-4 bg-linear-to-r from-[#175520] to-[#91C14D] rounded-4xl">
          <h1 className="font-extrabold">ONE BOTTLE AT A TIME</h1>
        </div>

        <div className="flex items-center justify-center w-full">
          <Image
            src="/images/arrows.png"
            alt="Stack of bottles"
            width={100}
            height={190}
            className="object-contain"
          />
        </div>

        <div className="flex flex-col text-[#114E1A] text-center border-2 p-3 rounded-3xl w-full justify-center gap-4ss">
          <p className="text-[3vh] font-medium">
            Note: Only 500ml plastic bottles are accepted
          </p>
          <p className="text-[2vh]">Property of Green Module Systems</p>
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

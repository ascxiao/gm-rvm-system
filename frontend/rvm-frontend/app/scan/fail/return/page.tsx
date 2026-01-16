import React from "react";
import Image from "next/image";

const Testing = () => {
  return (
    <div className="flex min-h-screen items-center justify-center font-sans text-[#8C0707]">
      <main className="flex min-h-screen w-full max-w-3xl flex-col p-8 bg-gray-200 gap-8 items-center justify-center ">
        <div className="flex rounded-4xl bg-[#C80B0E] px-6 pt-10 overflow-hidden w-[40vh] h-[50vh] justify-end">
          <Image
            src="/images/error.png"
            alt="Bottle"
            width={60}
            height={60}
            className="absolute"
          />
          <div className="flex rounded-t-3xl justify-center pt-6 pb-4 bg-[#4E1112] w-full h-full">
            <Image
              src="/images/failed.png"
              alt="Bottle"
              width={160}
              height={220}
              className="object-contain"
            />
          </div>
        </div>
        <div className="flex flex-col text-center justify-center">
          <span className="font-bold text-xl">FAILED!</span>
          <span className="font-medium text-md">
            Please put only 500ml plastic bottles
          </span>

          <span className="font-bold text-xl mt-2 animate-pulse">
            Returning...
          </span>
        </div>

        <span className="text-xs mt-2">Property of Green Module Systems</span>
      </main>
    </div>
  );
};

export default Testing;

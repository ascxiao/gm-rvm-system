import React from "react";
import Image from "next/image";

const Testing = () => {
  return (
    <div className="flex min-h-screen items-center justify-center font-sans text-[#3B9549]">
      <main className="flex min-h-screen w-full max-w-3xl flex-col p-8 bg-gray-200 gap-8 items-center justify-center ">
        <div className="flex rounded-4xl bg-[#3B9549] px-6 pt-10 overflow-hidden w-[40vh] h-[50vh] justify-center">
          <div className="flex rounded-t-3xl justify-center pt-6 pb-4 bg-[#114e1a] w-full h-full">
            <Image
              src="/images/Bottle.png"
              alt="Bottle"
              width={160}
              height={220}
              className="object-contain"
            />
          </div>
        </div>
        <span className="font-bold text-xl">SUCCESSFUL!</span>
        <span className="font-bold text-xl animate-pulse">
          Printing coupon...
        </span>
        <span className="text-xs mt-2">Property of Green Module Systems</span>
      </main>
    </div>
  );
};

export default Testing;

export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-200 gap-8 font-sans">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#078C10] border-t-gray-200" />
      <div className="flex flex-col items-center text-[#078C10]">
        <span className="animate-bounce font-bold">Scanning...</span>
        <span className="text-xs mt-8">Property of Green Module Systems</span>
      </div>
    </div>
  );
}

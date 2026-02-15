
import React from "react";
import { cn } from "./cn";

export default function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        "w-full px-3 py-2 rounded-2xl border border-lilac-200 bg-white focus-ring",
        className
      )}
      {...props}
    />
  );
}
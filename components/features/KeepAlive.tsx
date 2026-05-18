"use client";

import { useEffect } from "react";
import { startKeepAlive } from "@/lib/api";

export function KeepAlive() {
  useEffect(() => {
    startKeepAlive();
  }, []);
  return null; 
}
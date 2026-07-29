import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  transpilePackages: ["@restaurant-voice/shared-types"],
  // Monorepo: resolve deps from workspace root (npm hoist)
  outputFileTracingRoot: path.join(__dirname, "../.."),
  turbopack: {
    root: path.join(__dirname, "../.."),
  },
};

export default nextConfig;

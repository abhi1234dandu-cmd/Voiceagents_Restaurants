import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@restaurant-voice/shared-types"],
};

export default nextConfig;

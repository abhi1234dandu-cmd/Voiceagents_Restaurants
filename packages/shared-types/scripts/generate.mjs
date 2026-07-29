#!/usr/bin/env node
/**
 * Fetch OpenAPI from a running API and write a stub note.
 * Full codegen can be swapped to openapi-typescript later.
 */
const api = process.env.API_BASE_URL || "http://localhost:8000";
console.log(`Fetch OpenAPI from ${api}/openapi-export.json and sync packages/shared-types/src/index.ts`);
console.log("Hand-maintained types are the source of truth for this MVP.");

/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_GPX_DIR: string;
    readonly VITE_MAPTILER_KEY: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}

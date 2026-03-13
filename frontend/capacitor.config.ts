import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
    appId: 'com.codegenie.editor',
    appName: 'CodeGenie',
    webDir: 'dist',
    server: {
        // During development, use live reload from Vite dev server
        // url: 'http://YOUR_LOCAL_IP:5173',
        // cleartext: true,
        androidScheme: 'https',
    },
    plugins: {
        Keyboard: {
            resize: 'body',
            resizeOnFullScreen: true,
        },
        StatusBar: {
            style: 'dark',
            backgroundColor: '#0d1117',
        },
    },
};

export default config;

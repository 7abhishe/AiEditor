/**
 * CodeGenie — Platform Detection Utility
 * Detects whether the app is running in Electron, Capacitor (mobile), or plain web.
 */

export const isElectron = () =>
    typeof window !== 'undefined' && !!window.electronAPI;

export const isCapacitor = () =>
    typeof window !== 'undefined' && !!window.Capacitor;

export const isMobile = () => isCapacitor();
export const isDesktop = () => isElectron();
export const isWeb = () => !isElectron() && !isCapacitor();

/**
 * Returns 'electron' | 'capacitor' | 'web'
 */
export const getPlatform = () => {
    if (isElectron()) return 'electron';
    if (isCapacitor()) return 'capacitor';
    return 'web';
};

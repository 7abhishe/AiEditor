/**
 * CodeGenie — Adaptive Editor
 * Auto-selects Monaco (desktop/web) or CodeMirror (mobile) based on platform.
 * Lazy-loads each editor so only the necessary one is bundled per platform.
 */

import { lazy, Suspense } from 'react';
import { isMobile } from '../utils/platform';

const MonacoEditorWrapper = lazy(() => import('./editors/MonacoEditorWrapper'));
const MobileEditorWrapper = lazy(() => import('./editors/MobileEditorWrapper'));

export default function AdaptiveEditor(props) {
    return (
        <Suspense fallback={
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: 'var(--text-tertiary)',
                fontSize: '13px',
            }}>
                Loading editor…
            </div>
        }>
            {isMobile()
                ? <MobileEditorWrapper {...props} />
                : <MonacoEditorWrapper {...props} />
            }
        </Suspense>
    );
}

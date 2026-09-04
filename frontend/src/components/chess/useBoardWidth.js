import { useEffect, useRef, useState } from 'react';

/**
 * react-chessboard needs a numeric pixel width, so this measures its
 * wrapper element and keeps the board sized to fit, capped at `maxWidth`.
 */
export function useBoardWidth(maxWidth = 420) {
  const ref = useRef(null);
  const [width, setWidth] = useState(maxWidth);

  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    const update = () => setWidth(Math.max(200, Math.min(maxWidth, el.offsetWidth)));
    update();
    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, [maxWidth]);

  return [ref, width];
}

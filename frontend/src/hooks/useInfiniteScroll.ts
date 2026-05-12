import { useEffect, useRef } from 'react';

export function useInfiniteScroll(
  callback: () => void,
  enabled: boolean,
): React.RefObject<HTMLDivElement | null> {
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!enabled) return;
    const el = sentinelRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) callback();
      },
      { rootMargin: '200px' },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [callback, enabled]);

  return sentinelRef;
}

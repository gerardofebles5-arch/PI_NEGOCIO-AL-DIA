import { useEffect, useRef } from "react";

interface Props {
  clientId: string;
  onCredential: (credential: string) => void;
}

export function GoogleSignIn({ clientId, onCredential }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    const tryRender = () => {
      if (cancelled) return;
      if (window.google && ref.current) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: (resp) => onCredential(resp.credential),
        });
        ref.current.innerHTML = "";
        window.google.accounts.id.renderButton(ref.current, {
          type: "standard",
          theme: "filled_black",
          size: "large",
          text: "continue_with",
          shape: "pill",
          logo_alignment: "left",
          width: 300,
        });
      } else {
        setTimeout(tryRender, 250);
      }
    };
    tryRender();
    return () => {
      cancelled = true;
    };
  }, [clientId, onCredential]);

  return <div ref={ref} className="flex justify-center" />;
}

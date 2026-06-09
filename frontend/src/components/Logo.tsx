import logoPiNad from "../assets/logo-pinad.png";

export function Logo({ size = 40 }: { size?: number }) {
  return (
    <img
      src={logoPiNad}
      alt="(π)NAD — Administración y Asesoría en Negocios"
      height={size}
      style={{ height: size, width: "auto" }}
      className="select-none"
      draggable={false}
    />
  );
}

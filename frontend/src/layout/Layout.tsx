import type { ReactNode } from "react";

// Page shell: header, navigation, content area.
// Owner: hao

// TODO(hao): design the site layout (header, nav, responsive grid).
export default function Layout({ children }: { children: ReactNode }) {
  return <main>{children}</main>;
}

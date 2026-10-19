import type { ReactNode } from "react";

// Page shell: header, navigation, content area.
// Owner: member3

// TODO(member3): design the site layout (header, nav, responsive grid).
export default function Layout({ children }: { children: ReactNode }) {
  return <main>{children}</main>;
}

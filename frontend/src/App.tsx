import Layout from "./layout/Layout";
import DhtPanel from "./flows/DhtPanel";
import LightPanel from "./flows/LightPanel";
import RfidPanel from "./flows/RfidPanel";
import TimerForm from "./flows/TimerForm";
import LcdForm from "./flows/LcdForm";

// Root component. Renders every flow panel so each member can see their own
// work while developing.
// Owner: hao

// TODO(hao): add login/register pages (src/auth) and show the dashboard
// only to logged-in users; arrange the panels in the real layout.
export default function App() {
  return (
    <Layout>
      <DhtPanel />
      <LightPanel />
      <RfidPanel />
      <TimerForm />
      <LcdForm />
    </Layout>
  );
}

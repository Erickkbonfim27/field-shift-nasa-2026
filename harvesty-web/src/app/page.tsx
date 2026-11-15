import HarvestyApp from "@/components/HarvestyApp";
import { relevoMeta } from "@/lib/server/relevo";

export const runtime = "nodejs";

export default function Home() {
  const { bbox, classes } = relevoMeta();
  return <HarvestyApp relevo={{ bbox, classes }} />;
}

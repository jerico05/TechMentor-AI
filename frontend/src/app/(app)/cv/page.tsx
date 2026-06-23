import { redirect } from "next/navigation";

export default function CVRedirectPage() {
  redirect("/settings#settings-cv");
}

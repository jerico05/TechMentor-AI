import { redirect } from "next/navigation";

export default function ProfileRedirectPage() {
  redirect("/settings#settings-profile");
}

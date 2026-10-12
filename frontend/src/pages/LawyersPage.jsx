import PeopleManager from "../components/PeopleManager";

// Same length rules as backend/app/schemas/lawyer.py
const LAWYERS = {
  title: "Lawyers",
  singular: "Lawyer",
  endpoint: "/lawyers/",
  description: "Lawyers in your firm who can be assigned to cases.",
  limits: { name: [1, 255], phone: [5, 20] },
};

function LawyersPage() {
  return <PeopleManager config={LAWYERS} />;
}

export default LawyersPage;

import PeopleManager from "../components/PeopleManager";

// Same length rules as backend/app/schemas/client.py
const CLIENTS = {
  title: "Clients",
  singular: "Client",
  endpoint: "/clients/",
  description: "People and companies your firm represents.",
  limits: { name: [2, 225], phone: [1, 20] },
};

function ClientsPage() {
  return <PeopleManager config={CLIENTS} />;
}

export default ClientsPage;

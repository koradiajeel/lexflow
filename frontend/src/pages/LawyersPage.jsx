import CreateLoginButton from "../components/CreateLoginButton";
import PeopleManager from "../components/PeopleManager";

// Same length rules as backend/app/schemas/lawyer.py
const LAWYERS = {
  title: "Lawyers",
  singular: "Lawyer",
  endpoint: "/lawyers/",
  description: "Lawyers in your firm. Give a lawyer a login so they can sign in.",
  limits: { name: [1, 255], phone: [5, 20] },
  // Extra "Login" column: "Has login" badge or a "Create login" button.
  extraColumn: {
    header: "Login",
    render: (lawyer, { reload, showMessage }) => (
      <CreateLoginButton
        lawyer={lawyer}
        onCreated={(l) => {
          showMessage(`Login created for ${l.name}. They can now sign in with ${l.email}.`);
          reload();
        }}
      />
    ),
  },
};

function LawyersPage() {
  return <PeopleManager config={LAWYERS} />;
}

export default LawyersPage;

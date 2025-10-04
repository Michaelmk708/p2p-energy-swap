// src/components/RequireAuth.tsx
import { Navigate, useLocation } from "react-router-dom";
import { useUser } from "@/contexts/UserContext";

export default function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useUser();
  const loc = useLocation();

  if (loading) {
    return (
      <div className="min-h-[60vh] grid place-items-center text-muted-foreground">
        Checking your session…
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth" replace state={{ from: loc }} />;
  }

  return children;
}

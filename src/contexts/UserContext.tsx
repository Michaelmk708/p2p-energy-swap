import { createContext, useContext, useState, ReactNode } from "react";

export interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  location: string;
}

interface UserContextType {
  profile: UserProfile;
  updateProfile: (profile: UserProfile) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile>({
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    phone: "+254 712 345 678",
    location: "Nairobi, Kenya",
  });

  const updateProfile = (newProfile: UserProfile) => {
    setProfile(newProfile);
  };

  return (
    <UserContext.Provider value={{ profile, updateProfile }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within UserProvider");
  }
  return context;
}

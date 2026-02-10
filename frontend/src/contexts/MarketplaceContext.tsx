import { createContext, useContext, useState, ReactNode } from "react";

export interface Listing {
  id: string;
  tokens: number;
  pricePerToken: number;
  seller: string;
  createdAt: Date;
}

interface MarketplaceContextType {
  myListings: Listing[];
  addListing: (tokens: number, pricePerToken: number) => void;
  removeListing: (id: string) => void;
}

const MarketplaceContext = createContext<MarketplaceContextType | undefined>(undefined);

export function MarketplaceProvider({ children }: { children: ReactNode }) {
  const [myListings, setMyListings] = useState<Listing[]>([]);

  const addListing = (tokens: number, pricePerToken: number) => {
    const newListing: Listing = {
      id: Date.now().toString(),
      tokens,
      pricePerToken,
      seller: "johndoe_solar",
      createdAt: new Date(),
    };
    setMyListings((prev) => [newListing, ...prev]);
  };

  const removeListing = (id: string) => {
    setMyListings((prev) => prev.filter((listing) => listing.id !== id));
  };

  return (
    <MarketplaceContext.Provider value={{ myListings, addListing, removeListing }}>
      {children}
    </MarketplaceContext.Provider>
  );
}

export function useMarketplace() {
  const context = useContext(MarketplaceContext);
  if (!context) {
    throw new Error("useMarketplace must be used within MarketplaceProvider");
  }
  return context;
}

import { useState, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Zap, User, TrendingUp, Plus, ShoppingCart, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { useMarketplace } from "@/contexts/MarketplaceContext";
import { useNotifications } from "@/contexts/NotificationContext";
import { useSearchParams } from "react-router-dom";

// Dummy marketplace data
const marketListings = [
  { id: 1, seller: "SolarFarm_42", tokens: 50, pricePerToken: 12, rating: 4.8 },
  { id: 2, seller: "GreenHome_89", tokens: 25, pricePerToken: 11.5, rating: 4.9 },
  { id: 3, seller: "EcoVilla_23", tokens: 100, pricePerToken: 13, rating: 4.7 },
  { id: 4, seller: "SunnyRoof_15", tokens: 75, pricePerToken: 12.5, rating: 4.6 },
  { id: 5, seller: "WindPower_67", tokens: 40, pricePerToken: 11, rating: 5.0 },
];

export default function Marketplace() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [sellAmount, setSellAmount] = useState("");
  const [sellPrice, setSellPrice] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { myListings, addListing, removeListing } = useMarketplace();
  const { addNotification } = useNotifications();

  const activeTab = searchParams.get("tab") || "buy";

  useEffect(() => {
    if (searchParams.get("tab")) {
      // Tab is set from URL
    }
  }, [searchParams]);

  const handleListForSale = () => {
    if (!sellAmount || !sellPrice) {
      toast.error("Please fill in all fields");
      return;
    }
    
    const tokens = parseFloat(sellAmount);
    const price = parseFloat(sellPrice);
    
    addListing(tokens, price);
    toast.success(`Listed ${tokens} tokens at KES ${price} each`);
    setSellAmount("");
    setSellPrice("");
    setIsDialogOpen(false);
    
    // Switch to my-listings tab
    setSearchParams({ tab: "my-listings" });
  };

  const handleBuy = (listing: typeof marketListings[0]) => {
    toast.success(`Bought ${listing.tokens} tokens from ${listing.seller}`);
    addNotification({
      type: "buy",
      message: `You bought ${listing.tokens} tokens from ${listing.seller} for KES ${(listing.tokens * listing.pricePerToken).toFixed(2)}`,
    });
  };

  const handleRemoveListing = (id: string, tokens: number) => {
    removeListing(id);
    toast.success(`Removed listing for ${tokens} tokens`);
  };

  return (
    <Layout>
      <div className="space-y-6 animate-fade-in pb-20 md:pb-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Marketplace</h1>
            <p className="text-muted-foreground">Buy and sell energy tokens with your community</p>
          </div>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="energy" size="lg" className="w-full md:w-auto">
                <Plus className="mr-2 h-5 w-5" />
                List Tokens
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>List Tokens for Sale</DialogTitle>
                <DialogDescription>
                  Set your price and list your excess energy tokens
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div className="space-y-2">
                  <Label htmlFor="sell-amount">Number of Tokens</Label>
                  <Input
                    id="sell-amount"
                    type="number"
                    placeholder="e.g., 50"
                    value={sellAmount}
                    onChange={(e) => setSellAmount(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sell-price">Price per Token (KES)</Label>
                  <Input
                    id="sell-price"
                    type="number"
                    placeholder="e.g., 12"
                    value={sellPrice}
                    onChange={(e) => setSellPrice(e.target.value)}
                  />
                </div>
                {sellAmount && sellPrice && (
                  <div className="p-3 rounded-lg bg-muted">
                    <p className="text-sm text-muted-foreground">Total Listing Value</p>
                    <p className="text-2xl font-bold text-foreground">
                      KES {(parseFloat(sellAmount) * parseFloat(sellPrice)).toFixed(2)}
                    </p>
                  </div>
                )}
                <Button variant="energy" className="w-full" onClick={handleListForSale}>
                  List for Sale
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Market Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Average Price</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">KES 12.20</div>
              <p className="text-xs text-muted-foreground">per token</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Listings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">28</div>
              <p className="text-xs text-muted-foreground">active sellers</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>24h Volume</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">1,245</div>
              <p className="text-xs text-muted-foreground">tokens traded</p>
            </CardContent>
          </Card>
        </div>

        {/* Marketplace Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => setSearchParams({ tab: value })} className="space-y-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="buy">Buy Tokens</TabsTrigger>
            <TabsTrigger value="my-listings">My Listings</TabsTrigger>
          </TabsList>

          <TabsContent value="buy" className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {marketListings.map((listing) => (
                <Card key={listing.id} className="hover:shadow-lg transition-smooth">
                  <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                      <div className="flex items-start gap-4 flex-1">
                        <div className="p-3 rounded-lg bg-primary/10">
                          <User className="h-6 w-6 text-primary" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg text-foreground">{listing.seller}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="flex items-center gap-1">
                              <Zap className="h-3 w-3" />
                              {listing.tokens} tokens
                            </Badge>
                            <Badge variant="outline">⭐ {listing.rating}</Badge>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col md:flex-row items-start md:items-center gap-4 w-full md:w-auto">
                        <div className="text-left md:text-right">
                          <p className="text-sm text-muted-foreground">Price per token</p>
                          <p className="text-2xl font-bold text-foreground">KES {listing.pricePerToken}</p>
                          <p className="text-xs text-muted-foreground">
                            Total: KES {(listing.tokens * listing.pricePerToken).toFixed(2)}
                          </p>
                        </div>
                        <Button 
                          variant="energy" 
                          size="lg"
                          className="w-full md:w-auto"
                          onClick={() => handleBuy(listing)}
                        >
                          <ShoppingCart className="mr-2 h-4 w-4" />
                          Buy Now
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="my-listings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Your Active Listings</CardTitle>
                <CardDescription>Manage your token listings</CardDescription>
              </CardHeader>
              <CardContent>
                {myListings.length === 0 ? (
                  <div className="text-center py-8">
                    <Zap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground mb-4">No active listings</p>
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                      <DialogTrigger asChild>
                        <Button variant="outline">
                          <Plus className="mr-2 h-4 w-4" />
                          Create Your First Listing
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>List Tokens for Sale</DialogTitle>
                          <DialogDescription>
                            Set your price and list your excess energy tokens
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4 pt-4">
                          <div className="space-y-2">
                            <Label htmlFor="list-amount">Number of Tokens</Label>
                            <Input
                              id="list-amount"
                              type="number"
                              placeholder="e.g., 50"
                              value={sellAmount}
                              onChange={(e) => setSellAmount(e.target.value)}
                            />
                          </div>
                          <div className="space-y-2">
                            <Label htmlFor="list-price">Price per Token (KES)</Label>
                            <Input
                              id="list-price"
                              type="number"
                              placeholder="e.g., 12"
                              value={sellPrice}
                              onChange={(e) => setSellPrice(e.target.value)}
                            />
                          </div>
                          {sellAmount && sellPrice && (
                            <div className="p-3 rounded-lg bg-muted">
                              <p className="text-sm text-muted-foreground">Total Listing Value</p>
                              <p className="text-2xl font-bold text-foreground">
                                KES {(parseFloat(sellAmount) * parseFloat(sellPrice)).toFixed(2)}
                              </p>
                            </div>
                          )}
                          <Button variant="energy" className="w-full" onClick={handleListForSale}>
                            List for Sale
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {myListings.map((listing) => (
                      <div key={listing.id} className="p-4 rounded-lg border border-border hover:shadow-md transition-smooth">
                        <div className="flex items-center justify-between">
                          <div className="flex items-start gap-4 flex-1">
                            <div className="p-3 rounded-lg bg-primary/10">
                              <Zap className="h-6 w-6 text-primary" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg text-foreground">{listing.tokens} Tokens</h3>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge variant="secondary">
                                  KES {listing.pricePerToken} per token
                                </Badge>
                                <span className="text-sm text-muted-foreground">
                                  Total: KES {(listing.tokens * listing.pricePerToken).toFixed(2)}
                                </span>
                              </div>
                              <p className="text-xs text-muted-foreground mt-2">
                                Listed {new Date(listing.createdAt).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => handleRemoveListing(listing.id, listing.tokens)}
                            className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}

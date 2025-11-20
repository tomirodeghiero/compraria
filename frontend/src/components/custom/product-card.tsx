/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ProductCardProps {
  product: {
    id: string;
    nombre: string;
    categoria: string;
  };
  onAdd: (product: any) => void;
}

export default function ProductCard({ product, onAdd }: ProductCardProps) {
  return (
    <Card
      className="border border-border hover:border-accent transition-all duration-200 cursor-pointer group overflow-hidden"
      onClick={() => onAdd(product)}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-foreground text-sm line-clamp-2 group-hover:text-accent transition-colors">
              {product.nombre}
            </h3>
          </div>
          <Button
            size="icon"
            variant="ghost"
            className="h-8 w-8 flex-shrink-0 hover:bg-accent hover:text-accent-foreground"
            onClick={(e) => {
              e.stopPropagation();
              onAdd(product);
            }}
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
        <Badge variant="outline" className="text-xs">
          {product.categoria}
        </Badge>
      </CardContent>
    </Card>
  );
}

"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Minus, Trash2 } from "lucide-react";

interface CartItemProps {
  item: {
    producto: {
      id: string;
      nombre: string;
      categoria: string;
    };
    cantidad: number;
  };
  onChangeQty: (delta: number) => void;
  onRemove: () => void;
}

export default function CartItem({
  item,
  onChangeQty,
  onRemove,
}: CartItemProps) {
  return (
    <div className="bg-muted/50 border border-border rounded-lg p-4 hover:bg-muted transition-colors">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-foreground text-sm line-clamp-1">
            {item.producto.nombre}
          </h4>
          <Badge variant="outline" className="text-xs mt-1">
            {item.producto.categoria}
          </Badge>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            size="icon"
            variant="outline"
            className="h-8 w-8 bg-transparent"
            onClick={() => onChangeQty(-1)}
          >
            <Minus className="w-3 h-3" />
          </Button>
          <span className="font-bold w-8 text-center text-foreground">
            {item.cantidad}
          </span>
          <Button
            size="icon"
            variant="outline"
            className="h-8 w-8 bg-transparent"
            onClick={() => onChangeQty(1)}
          >
            <Plus className="w-3 h-3" />
          </Button>
        </div>
        <Button
          size="icon"
          variant="ghost"
          className="h-8 w-8 text-destructive hover:bg-destructive/10"
          onClick={onRemove}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}

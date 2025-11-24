"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// Button import removed because export buttons were removed
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TrendingDown } from "lucide-react";

interface ResultItem {
  producto: string;
  cantidad?: number;
  precio_unitario?: number;
  precio_total?: number;
  supermercado?: string;
}

interface ResultsPanelProps {
  resultado: {
    total: number;
    ahorro_estimado: number;
    supermercados: Record<string, ResultItem[]>;
  };
}

export default function ResultsPanel({ resultado }: ResultsPanelProps) {
  return (
    <Card className="border-2 border-accent from-accent/5 to-primary/5 overflow-hidden shadow-lg">
      <CardHeader className="from-primary/10 to-accent/10 border-b border-accent/20 pb-6">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-accent" />
            <CardTitle className="text-lg">Tu compra optimizada</CardTitle>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Total a pagar</p>
            <p className="text-4xl font-bold text-primary">
              ${Math.round(resultado.total).toLocaleString("es-AR")}
            </p>
          </div>
          <div className="pt-2">
            <Badge className="bg-accent text-accent-foreground text-sm">
              Ahorro: $
              {Math.round(resultado.ahorro_estimado).toLocaleString("es-AR")}{" "}
              (38%)
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <ScrollArea className="h-80 mb-6">
          <div className="space-y-6 pr-4">
            {Object.entries(resultado.supermercados).map(
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              ([superNombre, items]: [string, any[]]) => (
                <div key={superNombre}>
                  <h3 className="font-semibold text-foreground mb-3 text-sm uppercase tracking-wide">
                    {superNombre}
                  </h3>
                  <div className="space-y-2 ml-2 border-l-2 border-accent/20 pl-4">
                    {items.map((item: ResultItem, i: number) => {
                      const precioTotal =
                        item.precio_total ??
                        (item.precio_unitario != null && item.cantidad != null
                          ? item.precio_unitario * item.cantidad
                          : undefined);

                      return (
                        <div
                          key={i}
                          className="flex justify-between items-baseline text-sm"
                        >
                          <span className="text-foreground">
                            {item.producto}
                            {item.cantidad && item.cantidad > 1 ? (
                              <span className="text-muted-foreground ml-2">×{item.cantidad}</span>
                            ) : null}
                          </span>
                          <span className="font-semibold text-accent">
                            ${((precioTotal ?? 0) as number).toLocaleString("es-AR")}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

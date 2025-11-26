/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import {
  Search,
  ShoppingCart,
  Loader2,
  TrendingDown,
  Package,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Toaster, toast } from "sonner";
import Header from "@/components/custom/header";
import ProductCard from "@/components/custom/product-card";
import CartItem from "@/components/custom/cart-item";
import ResultsPanel from "@/components/custom/results-panel";

interface ProductoDB {
  id: string;
  nombre: string;
  categoria: string;
}

interface ItemCarrito {
  producto: ProductoDB;
  cantidad: number;
}

interface ResultadoOptimizacion {
  fecha: string;
  total: number;
  ahorro_estimado: number;
  porcentaje_ahorro: number;
  supermercados: Record<
    string,
    {
      producto: string;
      cantidad: number;
      precio_unitario: number;
      precio_total: number;
      supermercado: string;
    }[]
  >;
  resumen: string;
  estadisticas?: {
    productos_optimizados: number;
    unidades_totales: number;
    supermercados_usados: number;
    costo_peor_supermercado: number;
  };
  total_por_supermercado?: Record<string, number>;
}

export default function Home() {
  const [productosDB, setProductosDB] = useState<ProductoDB[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState("Todas");
  const [busqueda, setBusqueda] = useState("");
  const [carrito, setCarrito] = useState<ItemCarrito[]>([]);
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoOptimizacion | null>(
    null
  );
  const [totalProductosCount, setTotalProductosCount] = useState<number>(0);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await fetch(
          "/dataset_10000_productos_arg_5_super.csv"
        );
        const text = await response.text();
        const lines = text.split("\n");

        const header = lines[0].split(",");
        const nombreIndex = header.indexOf("nombre");
        const categoriaIndex = header.indexOf("categoria");

        if (nombreIndex === -1 || categoriaIndex === -1) {
          toast.error(
            "El CSV no tiene las columnas esperadas (nombre, categoria)"
          );
          return;
        }

        const productos: ProductoDB[] = [];
        const cats = new Set<string>();

        for (let i = 1; i < lines.length; i++) {
          const line = lines[i].trim();
          if (!line) continue;

          const cols = line.split(",");
          if (cols.length < header.length) continue;

          const nombreRaw = cols
            .slice(nombreIndex, categoriaIndex)
            .join(",")
            .trim();
          const categoria = cols[categoriaIndex]?.trim() || "Sin categoría";

          const nombre = nombreRaw.replace(/^"|"$/g, "").trim();

          const id = `prod_${i}`;

          productos.push({ id, nombre, categoria });
          cats.add(categoria);
        }

        setProductosDB(productos);
        setTotalProductosCount(productos.length);
        setCategorias(["Todas", ...Array.from(cats).sort()]);

        toast.success(`Cargados ${productos.length} productos.`);
      } catch (err) {
        console.error(err);
        toast.error(
          "No se encontró el CSV en /public/dataset_10000_productos_arg_5_super.csv"
        );
      }
    };

    loadProducts();
  }, []);

  const productosFiltrados = productosDB.filter(
    (p) =>
      (categoriaSeleccionada === "Todas" ||
        p.categoria === categoriaSeleccionada) &&
      p.nombre.toLowerCase().includes(busqueda.toLowerCase())
  );

  const agregar = (p: ProductoDB) => {
    setCarrito((prev) => {
      const existe = prev.find((i) => i.producto.id === p.id);
      if (existe) {
        toast(`+1 ${p.nombre}`);
        return prev.map((i) =>
          i.producto.id === p.id ? { ...i, cantidad: i.cantidad + 1 } : i
        );
      }
      toast(`Agregado: ${p.nombre}`);
      return [...prev, { producto: p, cantidad: 1 }];
    });
  };

  const cambiarCantidad = (id: string, delta: number) => {
    setCarrito((prev) =>
      prev
        .map((i) =>
          i.producto.id === id
            ? { ...i, cantidad: Math.max(0, i.cantidad + delta) }
            : i
        )
        .filter((i) => i.cantidad > 0)
    );
  };

  const optimizar = async () => {
    if (carrito.length === 0) return;
    setCargando(true);
    const loadingToast = toast.loading(
      "🧬 Algoritmo Genético buscando la mejor combinación..."
    );

    try {
      const payload = {
        productos: carrito.map((i) => ({
          nombre: i.producto.nombre,
          cantidad: i.cantidad,
        })),
        max_supermercados: 3,
      };

      const res = await axios.post<ResultadoOptimizacion>(
        "http://localhost:8000/api/optimizar",
        payload
      );

      setResultado(res.data);
      toast.dismiss(loadingToast);

      const stats = res.data.estadisticas;
      const ahorro = res.data.porcentaje_ahorro || 0;

      toast.success(
        `🎉 ¡Optimización completada! Total: $${Math.round(
          res.data.total
        ).toLocaleString("es-AR")}`,
        {
          description: `Ahorraste $${Math.round(
            res.data.ahorro_estimado
          ).toLocaleString("es-AR")} (${ahorro.toFixed(1)}%) usando ${
            stats?.supermercados_usados || "varios"
          } supermercados`,
          duration: 5000,
        }
      );
    } catch (err: any) {
      toast.dismiss(loadingToast);

      const errorMsg =
        err.response?.data?.detail ||
        "Backend no responde. Ejecutá: uvicorn server:app --reload";

      toast.error("Error en la optimización", {
        description: errorMsg,
        duration: 6000,
      });

      console.error("Error completo:", err);
    } finally {
      setCargando(false);
    }
  };

  // Export functions removed (PDF / WhatsApp) per UI requirements

  const totalItems = carrito.reduce((s, i) => s + i.cantidad, 0);

  const ahorroPromedio = resultado ? resultado.porcentaje_ahorro : 38;

  return (
    <>
      <Toaster position="top-center" richColors closeButton />
      <div className="min-h-screen from-background via-muted to-background">
        <Header />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-card rounded-lg border border-border p-6 text-center hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-center mb-3">
                <TrendingDown className="text-accent w-8 h-8" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {resultado ? "Tu Ahorro Real" : "Ahorro Promedio"}
              </p>
              <p className="text-3xl font-bold text-primary">
                {ahorroPromedio?.toFixed(1)}%
              </p>
              {resultado && (
                <p className="text-xs text-muted-foreground mt-1">
                  $
                  {Math.round(resultado.ahorro_estimado).toLocaleString(
                    "es-AR"
                  )}{" "}
                  ahorrados
                </p>
              )}
            </div>
            <div className="bg-card rounded-lg border border-border p-6 text-center hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-center mb-3">
                <Package className="text-accent w-8 h-8" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                Productos Disponibles
              </p>
              <p className="text-3xl font-bold text-primary">
                {totalProductosCount.toLocaleString()}
              </p>
              {resultado?.estadisticas && (
                <p className="text-xs text-muted-foreground mt-1">
                  {resultado.estadisticas.productos_optimizados} en tu carrito
                </p>
              )}
            </div>
            <div className="bg-card rounded-lg border border-border p-6 text-center hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-center mb-3">
                <Zap className="text-accent w-8 h-8" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                {resultado?.estadisticas
                  ? "Supermercados Usados"
                  : "Supermercados"}
              </p>
              <p className="text-3xl font-bold text-primary">
                {resultado?.estadisticas?.supermercados_usados || 5}
              </p>
              {!resultado && (
                <p className="text-xs text-muted-foreground mt-1">
                  Disponibles para optimizar
                </p>
              )}
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Catálogo */}
            <div className="lg:col-span-2">
              <Card className="border border-border overflow-hidden shadow-sm">
                <CardHeader className="from-primary/5 to-accent/5 border-b border-border py-6">
                  <div className="space-y-4">
                    <div>
                      <h2 className="text-xl font-semibold text-foreground mb-4">
                        Busca y agrega productos
                      </h2>
                      <div className="flex gap-3">
                        <Select
                          value={categoriaSeleccionada}
                          onValueChange={setCategoriaSeleccionada}
                        >
                          <SelectTrigger className="w-full sm:w-48 bg-background border-border">
                            <SelectValue placeholder="Categoría" />
                          </SelectTrigger>
                          <SelectContent>
                            {categorias.map((c) => (
                              <SelectItem key={c} value={c}>
                                {c}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="relative">
                      <Search className="absolute left-3 top-3 text-muted-foreground w-5 h-5" />
                      <Input
                        placeholder="Busca entre 10.000 productos..."
                        value={busqueda}
                        onChange={(e) => setBusqueda(e.target.value)}
                        className="pl-10 bg-background border-border text-foreground placeholder-muted-foreground"
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  <ScrollArea className="h-[600px]">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pr-4">
                      {productosFiltrados.length > 0 ? (
                        productosFiltrados.map((p) => (
                          <ProductCard key={p.id} product={p} onAdd={agregar} />
                        ))
                      ) : (
                        <div className="col-span-2 text-center py-12">
                          <p className="text-muted-foreground">
                            No se encontraron productos con esos criterios
                          </p>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

            {/* Carrito y Resultado */}
            <div className="space-y-8">
              <Card className="border border-border overflow-hidden shadow-sm">
                <CardHeader className="from-primary/5 to-accent/5 border-b border-border py-6">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <ShoppingCart className="w-5 h-5 text-accent" />
                    Mi Carrito
                    <Badge variant="secondary" className="ml-auto">
                      {totalItems}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <ScrollArea className="h-80">
                    <div className="space-y-3 pr-4">
                      {carrito.length === 0 ? (
                        <div className="text-center py-8">
                          <ShoppingCart className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
                          <p className="text-sm text-muted-foreground">
                            Agrega productos para empezar
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            El algoritmo genético los optimizará
                          </p>
                        </div>
                      ) : (
                        carrito.map((i) => (
                          <CartItem
                            key={i.producto.id}
                            item={i}
                            onChangeQty={(delta) =>
                              cambiarCantidad(i.producto.id, delta)
                            }
                            onRemove={() =>
                              cambiarCantidad(i.producto.id, -i.cantidad)
                            }
                          />
                        ))
                      )}
                    </div>
                  </ScrollArea>

                  <Button
                    onClick={optimizar}
                    disabled={cargando || carrito.length === 0}
                    className="w-full h-12 text-base font-semibold mt-6 bg-primary hover:bg-primary/90 transition-all"
                  >
                    {cargando ? (
                      <>
                        <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                        Optimizando con AG...
                      </>
                    ) : (
                      <>
                        <Zap className="mr-2 w-4 h-4" />
                        Optimizar con Genético
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {resultado && <ResultsPanel resultado={resultado} />}
            </div>
          </div>
        </main>
      </div>
    </>
  );
}

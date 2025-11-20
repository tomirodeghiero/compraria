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

export default function Home() {
  const [productosDB, setProductosDB] = useState<ProductoDB[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState("Todas");
  const [busqueda, setBusqueda] = useState("");
  const [carrito, setCarrito] = useState<ItemCarrito[]>([]);
  const [cargando, setCargando] = useState(false);
  const [resultado, setResultado] = useState<{
    total: number;
    ahorro_estimado: number;
    supermercados: Record<string, { producto: string; precio: number }[]>;
  } | null>(null);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await fetch(
          "/dataset_10000_productos_arg_5_super.csv"
        );
        const text = await response.text();
        const lines = text.split("\n").slice(1);

        const productosUnicos = new Map<string, ProductoDB>();
        const cats = new Set<string>();

        lines.forEach((line) => {
          if (!line.trim()) return;
          const cols = line.split(",");
          if (cols.length < 8) return;

          const id = cols[0];
          let nombre = cols[1].trim();
          const categoria = cols[2].trim();

          nombre = nombre.replace(/ x\d+$/i, "").trim();

          const clave = `${nombre.toLowerCase()}|${categoria.toLowerCase()}`;

          if (!productosUnicos.has(clave)) {
            productosUnicos.set(clave, { id, nombre, categoria });
            cats.add(categoria);
          }
        });

        const productos = Array.from(productosUnicos.values());
        setProductosDB(productos);
        setCategorias(["Todas", ...Array.from(cats).sort()]);
        toast.success(
          `¡Cargados ${productos.length.toLocaleString()} productos únicos!`
        );
      } catch (err) {
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
    toast.loading("Buscando las mejores ofertas...");

    try {
      const payload = {
        productos: carrito.map((i) => ({
          nombre: i.producto.nombre,
          cantidad: i.cantidad,
        })),
        max_supermercados: 3,
      };

      const res = await axios.post(
        "http://localhost:8000/api/optimizar",
        payload
      );
      setResultado(res.data);
      toast.dismiss();
      toast.success(
        `¡AHORRADOR! Total: $${Math.round(res.data.total).toLocaleString(
          "es-AR"
        )}`
      );
    } catch (err: any) {
      toast.dismiss();
      toast.error(
        err.response?.data?.detail ||
          "Backend no responde. Ejecutá uvicorn server:app --reload"
      );
    } finally {
      setCargando(false);
    }
  };

  const descargarPDF = async () => {
    if (!resultado) return;
    toast.loading("Generando PDF...");
    try {
      const res = await axios.post(
        "http://localhost:8000/api/generar-pdf",
        resultado,
        { responseType: "blob" }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `Compra_Ahorro_${new Date().toISOString().slice(0, 10)}.pdf`;
      a.click();
      toast.dismiss();
      toast.success("¡PDF descargado!");
    } catch {
      toast.dismiss();
      toast.error("Error generando PDF");
    }
  };

  const compartirWhatsApp = async () => {
    if (!resultado) return;
    toast.loading("Abriendo WhatsApp...");
    try {
      const res = await axios.post(
        "http://localhost:8000/api/generar-whatsapp",
        resultado
      );
      window.open(res.data.url, "_blank");
      toast.dismiss();
      toast.success("¡Listo para compartir!");
    } catch {
      toast.dismiss();
      toast.error("Error generando link");
    }
  };

  const totalItems = carrito.reduce((s, i) => s + i.cantidad, 0);

  return (
    <>
      <Toaster position="top-center" richColors closeButton />
      <div className="min-h-screen bg-gradient-to-b from-background via-muted to-background">
        <Header />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Hero Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-card rounded-lg border border-border p-6 text-center">
              <div className="flex items-center justify-center mb-3">
                <TrendingDown className="text-accent w-8 h-8" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                Ahorro Promedio
              </p>
              <p className="text-3xl font-bold text-primary">38%</p>
            </div>
            <div className="bg-card rounded-lg border border-border p-6 text-center">
              <div className="flex items-center justify-center mb-3">
                <Package className="text-accent w-8 h-8" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                Productos
              </p>
              <p className="text-3xl font-bold text-primary">
                {productosDB.length.toLocaleString()}
              </p>
            </div>
            <div className="bg-card rounded-lg border border-border p-6 text-center">
              <div className="flex items-center justify-center mb-3">
                <Zap className="text-accent w-8 h-8" />
              </div>
              <p className="text-sm font-medium text-muted-foreground mb-1">
                Supermercados
              </p>
              <p className="text-3xl font-bold text-primary">5</p>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Catálogo */}
            <div className="lg:col-span-2">
              <Card className="border border-border overflow-hidden shadow-sm">
                <CardHeader className="bg-gradient-to-r from-primary/5 to-accent/5 border-b border-border py-6">
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
                      {productosFiltrados.map((p) => (
                        <ProductCard key={p.id} product={p} onAdd={agregar} />
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>

            {/* Carrito y Resultado */}
            <div className="space-y-8">
              <Card className="border border-border overflow-hidden shadow-sm">
                <CardHeader className="bg-gradient-to-r from-primary/5 to-accent/5 border-b border-border py-6">
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
                          <p className="text-sm text-muted-foreground">
                            Agrega productos para empezar
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
                    className="w-full h-12 text-base font-semibold mt-6 bg-primary hover:bg-primary/90"
                  >
                    {cargando ? (
                      <>
                        <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                        Optimizando...
                      </>
                    ) : (
                      <>
                        <Zap className="mr-2 w-4 h-4" />
                        Optimizar Compra
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {resultado && (
                <ResultsPanel
                  resultado={resultado}
                  onDownloadPDF={descargarPDF}
                  onShareWhatsApp={compartirWhatsApp}
                />
              )}
            </div>
          </div>
        </main>
      </div>
    </>
  );
}

export default function Header() {
  return (
    <header className="border-b border-border bg-card sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground">Compraria</h1>
            <p className="text-xs text-muted-foreground">
              Optimizador de compras
            </p>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">🇦🇷 Argentina</p>
      </div>
    </header>
  );
}

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.38.4'

serve(async (req) => {
  try {
    const { file, filename, options } = await req.json()
    
    if (!file || !filename) {
      return new Response(
        JSON.stringify({ error: 'Missing file or filename' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Simulación de OCR Ultra con datos realistas
    // En producción, esto se conectaría a un servicio real de OCR
    const mockOCRResult = {
      document_type: "Factura",
      confidence: 0.95,
      date: new Date().toISOString().split('T')[0],
      amount: 1500.00,
      tax: 240.00,
      total: 1740.00,
      vendor: "Proveedor Demo S.A.",
      invoice_number: "FAC-" + Math.floor(Math.random() * 10000),
      items: [
        { description: "Servicio Consultoría", quantity: 1, unit_price: 1000.00, amount: 1000.00 },
        { description: "Licencia Software", quantity: 1, unit_price: 500.00, amount: 500.00 }
      ],
      tables: [
        [
          ["Descripción", "Cantidad", "Precio Unitario", "Monto"],
          ["Servicio Consultoría", "1", "1000.00", "1000.00"],
          ["Licencia Software", "1", "500.00", "500.00"],
          ["Subtotal", "", "", "1500.00"],
          ["IVA (16%)", "", "", "240.00"],
          ["Total", "", "", "1740.00"]
        ]
      ],
      signatures: [
        { location: "bottom-right", confidence: 0.92, bounding_box: { x: 800, y: 1000, width: 200, height: 100 } }
      ],
      qr_codes: [
        { data: "https://demo.com/qr/12345", location: "top-right", confidence: 0.98 }
      ],
      barcodes: [
        { data: "1234567890123", type: "EAN-13", location: "bottom-left", confidence: 0.95 }
      ],
      layout: {
        width: 2100,
        height: 2970,
        orientation: "portrait",
        regions: [
          { type: "header", x: 0, y: 0, width: 2100, height: 400 },
          { type: "body", x: 0, y: 400, width: 2100, height: 2200 },
          { type: "footer", x: 0, y: 2600, width: 2100, height: 370 }
        ]
      },
      text: "FACTURA\nProveedor Demo S.A.\nRIF: J-123456789-0\nFecha: " + new Date().toISOString().split('T')[0] + "\n\nDescripción\tCantidad\tPrecio\tMonto\nServicio Consultoría\t1\t1000.00\t1000.00\nLicencia Software\t1\t500.00\t500.00\n\nSubtotal: 1500.00\nIVA (16%): 240.00\nTotal: 1740.00",
      language: "es",
      processing_time: 2.5
    }

    return new Response(
      JSON.stringify(mockOCRResult),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})

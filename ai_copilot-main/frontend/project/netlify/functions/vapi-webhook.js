const { createClient } = require('@supabase/supabase-js')
const { GoogleGenerativeAI } = require("@google/generative-ai")

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_ANON_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

// Initialize Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)

const extractStructuredData = async (payload) => {
  console.log('[DEBUG] Starting structured data extraction')
  
  const model = genAI.getGenerativeModel({ model: "gemini-2.5-pro" })
  const prompt = `Extract the following information from this conversation summary and transcript. Return ONLY a JSON object with these fields:
  {
    "doctor": {
      "name": string or null,
      "specialization": string,
      "email": null,
      "phoneNumber": null
    },
    "patient": {
      "name": string,
      "dob": string,
      "phoneNumber": null
    },
    "hospital": {
      "name": "CityCare Hospital",
      "address": "123 Main St, Dallas, TX",
      "phoneNumber": null
    },
    "appointment": {
      "date": string (YYYY-MM-DD format),
      "startTime": string (HH:MM format),
      "endTime": string (HH:MM format, 30 minutes after startTime)
    }
  }

  Summary: ${payload.message.analysis.summary}
  
  Relevant transcript excerpts:
  ${payload.message.transcript}
  
  Additional context:
  - If no specific doctor is assigned, use "Available Doctor" as the name
  - Convert times to 24-hour format
  - The current year is 2025
  - Appointment duration is 30 minutes`

  try {
    const result = await model.generateContent(prompt)
    const response = await result.response
    const text = response.text()
    console.log('[DEBUG] Structured data:', text)
    
    return JSON.parse(text)
  } catch (error) {
    console.error('[ERROR] Structured data extraction failed:', error)
    throw error
  }
}

const insertHospitalData = async (hospitalData) => {
  console.log('[DEBUG] Inserting/Getting hospital data')
  let { data: hospital, error } = await supabase
    .from('Hospital')
    .select('HospitalID')
    .eq('HospitalName', hospitalData.name)
    .single()

  if (error || !hospital) {
    const { data: newHospital, error: insertError } = await supabase
      .from('Hospital')
      .insert([hospitalData])
      .select()
      .single()

    if (insertError) throw insertError
    hospital = newHospital
  }

  return hospital
}

const insertDoctorData = async (doctorData) => {
  console.log('[DEBUG] Inserting/Getting doctor data')
  let { data: doctor, error } = await supabase
    .from('Doctor')
    .select('DoctorID')
    .eq('Specialization', doctorData.specialization)
    .eq('DoctorName', doctorData.name)
    .single()

  if (error || !doctor) {
    const { data: newDoctor, error: insertError } = await supabase
      .from('Doctor')
      .insert([doctorData])
      .select()
      .single()

    if (insertError) throw insertError
    doctor = newDoctor
  }

  return doctor
}

const insertPatientData = async (patientData) => {
  console.log('[DEBUG] Inserting/Getting patient data')
  let { data: patient, error } = await supabase
    .from('Patient')
    .select('PatientID')
    .eq('PatientName', patientData.name)
    .single()

  if (error || !patient) {
    const { data: newPatient, error: insertError } = await supabase
      .from('Patient')
      .insert([patientData])
      .select()
      .single()

    if (insertError) throw insertError
    patient = newPatient
  }

  return patient
}

const insertAppointmentData = async (appointmentData, doctorId, patientId) => {
  console.log('[DEBUG] Inserting appointment data')
  const { data: appointment, error } = await supabase
    .from('Appointments')
    .insert([{
      DoctorID: doctorId,
      PatientID: patientId,
      Date: appointmentData.date,
      StartTime: appointmentData.startTime,
      EndTime: appointmentData.endTime
    }])
    .select()
    .single()

  if (error) throw error
  return appointment
}

const insertDoctorAvailability = async (doctorId, appointmentData) => {
  console.log('[DEBUG] Updating doctor availability')
  const { data: availability, error } = await supabase
    .from('DoctorAvailability')
    .insert([{
      DoctorID: doctorId,
      Date: appointmentData.date,
      StartTime: appointmentData.startTime,
      EndTime: appointmentData.endTime
    }])
    .select()
    .single()

  if (error) throw error
  return availability
}

exports.handler = async (event, context) => {
  console.log('[DEBUG] Webhook received')
  
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' }
  }

  try {
    const payload = JSON.parse(event.body || '')
    console.log('[DEBUG] Webhook payload type:', payload.message.type)

    if (payload.message.type !== 'end-of-call-report') {
      return { 
        statusCode: 400, 
        body: JSON.stringify({ error: 'Invalid webhook type' })
      }
    }

    // Extract structured data using Gemini
    const structuredData = await extractStructuredData(payload)
    
    // Insert data into Supabase tables
    const hospital = await insertHospitalData(structuredData.hospital)
    const doctor = await insertDoctorData(structuredData.doctor)
    const patient = await insertPatientData(structuredData.patient)
    const appointment = await insertAppointmentData(
      structuredData.appointment,
      doctor.DoctorID,
      patient.PatientID
    )
    const availability = await insertDoctorAvailability(
      doctor.DoctorID,
      structuredData.appointment
    )

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Webhook processed successfully',
        data: {
          structuredData,
          dbResults: {
            hospital,
            doctor,
            patient,
            appointment,
            availability
          },
          recordingUrl: payload.message.recording_url,
          callDuration: payload.message.duration_seconds,
          endReason: payload.message.ended_reason
        }
      })
    }
  } catch (error) {
    console.error('[ERROR] Processing webhook:', error)
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        error: 'Internal server error',
        details: error.message
      })
    }
  }
}
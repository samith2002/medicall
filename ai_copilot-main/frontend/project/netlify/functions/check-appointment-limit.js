const { createClient } = require('@supabase/supabase-js');

// Environment variable validation
const requiredEnvVars = {
  SUPABASE_URL: process.env.SUPABASE_URL,
  SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY,
};

const missingVars = Object.entries(requiredEnvVars)
  .filter(([_, value]) => !value)
  .map(([key]) => key);

if (missingVars.length > 0) {
  throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
}

// Initialize Supabase client
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

// Check appointment limit (max 5 per date)
const checkAppointmentLimit = async (doctorName, date) => {
  console.log('[DEBUG] Checking appointment limit');
  try {
    // Step 1: Get the doctor's ID
    const { data: doctor, error: doctorError } = await supabase
      .from('doctor')
      .select('doctorid')
      .eq('doctorname', doctorName)
      .single();

    if (doctorError || !doctor) {
      console.error('[ERROR] Doctor not found:', doctorName, doctorError?.message);
      throw new Error(`Doctor not found: ${doctorName}`);
    }

    // Step 2: Count appointments for the doctor on the given date
    const { count, error: countError } = await supabase
      .from('appointments')
      .select('*', { count: 'exact', head: true })
      .eq('doctorid', doctor.doctorid)
      .eq('date', date);

    if (countError) {
      console.error('[ERROR] Failed to count appointments:', countError.message);
      throw new Error(`Failed to count appointments: ${countError.message}`);
    }

    console.log('[DEBUG] Appointment count for doctor on date:', { doctorName, date, count });
    const maxAppointments = 5;
    if (count >= maxAppointments) {
      return {
        canSchedule: false,
        message: `${doctorName} has reached the maximum of ${maxAppointments} appointments on ${date}. Please choose another date.`,
      };
    }

    return {
      canSchedule: true,
      message: `${doctorName} can schedule an appointment on ${date}.`,
    };
  } catch (error) {
    console.error('[ERROR] Check appointment limit failed:', error.message);
    throw error;
  }
};

exports.handler = async (event) => {
  console.log('[DEBUG] Check appointment limit webhook received');

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const payload = JSON.parse(event.body || '');
    console.log('[DEBUG] Payload:', payload);

    if (payload.type !== 'function-call' || !payload.functionCall) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Invalid request type, expected function-call' }),
      };
    }

    const { name, parameters, toolCallId } = payload.functionCall;
    console.log('[DEBUG] Function call:', { name, parameters, toolCallId });

    if (name !== 'checkAppointmentLimit') {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: `Invalid function name: ${name}, expected checkAppointmentLimit` }),
      };
    }

    if (!parameters.doctorName || !parameters.date) {
      throw new Error('doctorName and date are required');
    }

    const result = await checkAppointmentLimit(parameters.doctorName, parameters.date);

    return {
      statusCode: 200,
      body: JSON.stringify({
        toolCallId,
        result,
      }),
    };
  } catch (error) {
    console.error('[ERROR] Processing check appointment limit webhook:', error.message, error.stack);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message,
      }),
    };
  }
};
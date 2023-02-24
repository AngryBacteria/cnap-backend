export async function asyncWrap(promise: Promise<any>): Promise<{ data: any; error: any }> {
  try {
    const data = await promise;
    return { data: data, error: null };
  } catch (error) {
    return { data: null, error: error };
  }
}

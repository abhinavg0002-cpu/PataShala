import React from 'react';
import { ReportView } from './Report';
export default function Result({ params }: { params: any }) { return <ReportView subject={params.subject} name={params.name} reveal />; }

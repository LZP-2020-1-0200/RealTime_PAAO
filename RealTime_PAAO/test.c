#include <complex.h>
#include <stdio.h>

#define PI 3.14159265359

void display_matrix(double complex mat[2][2], int rows, int cols)
{
    for (int i = 0; i < rows; ++i)
    {
        printf("\n");
        for (int j = 0; j < cols; ++j)
        {
            printf("%.5f %+.5fi\t", creal((mat[i][j])), cimag((mat[i][j])));
        }
    }
    printf("\n");
}

void mat_mul_2x_2(double complex first[2][2],
                  double complex second[2][2],
                  double complex result[2][2],
                  int r1, int c1, int r2, int c2)
{
    for (int i = 0; i < r1; ++i)
    {
        for (int j = 0; j < c2; ++j)
        {
            result[i][j] = 0;
        }
    }

    for (int i = 0; i < r1; ++i)
    {
        for (int j = 0; j < c2; ++j)
        {
            for (int k = 0; k < c1; ++k)
            {
                result[i][j] += first[i][k] * second[k][j];
            }
        }
    }
}

void mat_mul_2x_1(double complex first[2][2],
                  double complex second[2][1],
                  double complex result[2][1],
                  int r1, int c1, int r2, int c2)
{
    for (int i = 0; i < r1; ++i)
    {
        for (int j = 0; j < c2; ++j)
        {
            result[i][j] = 0;
        }
    }
    for (int i = 0; i < r1; ++i)
    {
        for (int j = 0; j < c2; ++j)
        {
            for (int k = 0; k < c1; ++k)
            {
                result[i][j] += first[i][k] * second[k][j];
            }
        }
    }
}

double complex wrapper(double real, double imag)
{
    return real + imag * I;
}

void multilayer(double n_water[321], double k_water[321],
                double n_al203[321], double k_al203[321],
                double n_al[321], double k_al[321],
                double R[321], double wavelength[321],
                double thickness, double normalization)
{

    double complex nk_water_[321];
    double complex nk_al203_[321];
    double complex nk_al_[321];
    for (int i = 0; i < 321; i++)
    {
        nk_water_[i] = wrapper(n_water[i], k_water[i]);
        nk_al203_[i] = wrapper(n_al203[i], k_al203[i]);
        nk_al_[i] = wrapper(n_al[i], k_al[i]);
    }
    int length = 321;
    for (int a = 0; a < length; a++)
    {
        double complex nk[] = {nk_water_[a], nk_al203_[a], nk_al_[a]};
        double complex tau = 2 * nk[0] / (nk[0] + nk[1]);
        double complex rho = (nk[0] - nk[1]) / (nk[0] + nk[1]);
        double complex T[2][2] = {{(1 + 0 * I) / tau, rho / tau}, {rho / tau, (1 + 0 * I) / tau}};
        double complex mat_mul_result[2][2];
        double complex M[2][2] = {{1 + 0 * I, 0 + 0 * I},{0 + 0 * I, 1 + 0 * I}};
        mat_mul_2x_2(M, T, mat_mul_result, 2, 2, 2, 2);
        double complex k = nk[1] * 2 * PI / wavelength[a];
        double complex P[2][2] = {{cexp((0 + 1 * I) * k * thickness), 0},
                                  {0, cexp(-(0 + 1 * I) * k * thickness)}};
        double complex mat_mul_result2[2][2];
        mat_mul_2x_2(mat_mul_result, P, mat_mul_result2, 2, 2, 2, 2);
        double complex Ef[2][1] = {{1 + 0 * I},{(nk[1] - nk[2]) / (nk[1] + nk[2])}};
        double complex E0[2][1];
        mat_mul_2x_1(mat_mul_result2, Ef, E0, 2, 2, 2, 1);
        double result = cabs(E0[0][1] / E0[0][0]);
        R[a] = result * result * normalization;
    }
}

void multilayer(double complex nk_water[321],
                double complex nk_al203[321],
                double complex nk_al[321],
                double R[321], double wavelength[321],
                double thickness, double normalization)
{
    int length = 321;
    for (int a = 0; a < length; a++)
    {
        double complex nk[] = {nk_water[a], nk_al203[a], nk_al[a]};
        double complex tau = 2 * nk[0] / (nk[0] + nk[1]);
        double complex rho = (nk[0] - nk[1]) / (nk[0] + nk[1]);
        double complex T[2][2] = {{(1 + 0 * I) / tau, rho / tau}, {rho / tau, (1 + 0 * I) / tau}};
        double complex mat_mul_result[2][2];
        double complex M[2][2] = {{1 + 0 * I, 0 + 0 * I}, {0 + 0 * I, 1 + 0 * I}};
        mat_mul_2x_2(M, T, mat_mul_result, 2, 2, 2, 2);
        double complex k = nk[1] * 2 * PI / wavelength[a];
        double complex P[2][2] = {{cexp((0 + 1 * I) * k * thickness), 0},
                                  {0, cexp(-(0 + 1 * I) * k * thickness)}};
        double complex mat_mul_result2[2][2];
        mat_mul_2x_2(mat_mul_result, P, mat_mul_result2, 2, 2, 2, 2);
        double complex Ef[2][1] = {{1 + 0 * I}, {(nk[1] - nk[2]) / (nk[1] + nk[2])}};
        double complex E0[2][1];
        mat_mul_2x_1(mat_mul_result2, Ef, E0, 2, 2, 2, 1);
        double result = cabs(E0[0][1] / E0[0][0]);
        R[a] = result * result * normalization;
    }
}
